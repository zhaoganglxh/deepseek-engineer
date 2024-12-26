#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path
from textwrap import dedent
from typing import List, Dict, Any, Optional
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.style import Style

# Initialize Rich console
console = Console()

# --------------------------------------------------------------------------------
# 1. Configure OpenAI client and load environment variables
# --------------------------------------------------------------------------------
load_dotenv()  # Load environment variables from .env file
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)  # Configure for DeepSeek API

# --------------------------------------------------------------------------------
# 2. Define our schema using Pydantic for type safety
# --------------------------------------------------------------------------------
class FileToCreate(BaseModel):
    path: str
    content: str

# NEW: Diff editing structure
class FileToEdit(BaseModel):
    path: str
    original_snippet: str
    new_snippet: str

class AssistantResponse(BaseModel):
    assistant_reply: str
    files_to_create: Optional[List[FileToCreate]] = None
    # NEW: optionally hold diff edits
    files_to_edit: Optional[List[FileToEdit]] = None

# --------------------------------------------------------------------------------
# 3. system prompt
# --------------------------------------------------------------------------------
system_PROMPT = dedent("""\
    You are a coding assistant that can:
      - Chat about code,
      - Read user-provided file contents for context,
      - Generate or overwrite files on the user's filesystem.

    You must output valid JSON that matches this schema:
    {
      "assistant_reply": "your main text or conversational answer",
      "files_to_create": [
        {
          "path": "path/to/file",
          "content": "file content"
        }
      ],
      "files_to_edit": [
        {
          "path": "path/to/file",
          "original_snippet": "the text you want replaced",
          "new_snippet": "the text that replaces it"
        }
      ]
    }

    Behaviors:
      - If you want to provide normal chat text, do so in 'assistant_reply'.
      - If the user requests code or multiple files, include them in 'files_to_create'.
      - If you want to edit existing files, use 'files_to_edit'.
      - If no files need to be created or edited, omit the corresponding fields or pass empty arrays.
""")

# --------------------------------------------------------------------------------
# 4. Helper functions 
# --------------------------------------------------------------------------------

def read_local_file(file_path: str) -> str:
    """Return the text content of a local file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def create_file(path: str, content: str):
    """Create (or overwrite) a file at 'path' with the given 'content'."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)  # ensures any dirs exist
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"[green]✓[/green] Created/updated file at '[cyan]{file_path}[/cyan]'")

# NEW: Show the user a table of proposed edits and confirm
def show_diff_table(files_to_edit: List[FileToEdit]) -> None:
    if not files_to_edit:
        return
    
    # Enable multi-line rows by setting show_lines=True
    table = Table(title="Proposed Edits", show_header=True, header_style="bold magenta", show_lines=True)
    table.add_column("File Path", style="cyan")
    table.add_column("Original", style="red")
    table.add_column("New", style="green")

    for edit in files_to_edit:
        # Removed snippet truncation so entire text is displayed
        table.add_row(edit.path, edit.original_snippet, edit.new_snippet)
    
    console.print(table)

# NEW: Apply diff edits
def apply_diff_edit(path: str, original_snippet: str, new_snippet: str):
    """Reads the file at 'path', replaces the first occurrence of 'original_snippet' with 'new_snippet', then overwrites."""
    try:
        content = read_local_file(path)
        if original_snippet in content:
            updated_content = content.replace(original_snippet, new_snippet, 1)
            create_file(path, updated_content)
            console.print(f"[green]✓[/green] Applied diff edit to '[cyan]{path}[/cyan]'")
        else:
            console.print(f"[yellow]⚠[/yellow] Original snippet not found in '[cyan]{path}[/cyan]'. No changes made.", style="yellow")
    except FileNotFoundError:
        console.print(f"[red]✗[/red] File not found for diff editing: '[cyan]{path}[/cyan]'", style="red")

def try_handle_add_command(user_input: str) -> bool:
    """
    If user_input starts with '/add ', read that file and insert its content
    into conversation as a system message. Returns True if handled; else False.
    """
    prefix = "/add "
    if user_input.strip().lower().startswith(prefix):
        file_path = user_input[len(prefix):].strip()
        try:
            content = read_local_file(file_path)
            conversation_history.append({
                "role": "system",
                "content": f"Content of file '{file_path}':\n\n{content}"
            })
            console.print(f"[green]✓[/green] Added file '[cyan]{file_path}[/cyan]' to conversation.\n")
        except OSError as e:
            console.print(f"[red]✗[/red] Could not add file '[cyan]{file_path}[/cyan]': {e}\n", style="red")
        return True
    return False

# --------------------------------------------------------------------------------
# 5. Conversation state
# --------------------------------------------------------------------------------
conversation_history = [
    {"role": "system", "content": system_PROMPT}
]

# --------------------------------------------------------------------------------
# 6. OpenAI API interaction with streaming
# --------------------------------------------------------------------------------

def stream_openai_response(user_message: str):
    """
    Streams the DeepSeek chat completion response and handles structured output.
    Returns the final AssistantResponse.
    """
    conversation_history.append({"role": "user", "content": user_message})

    full_content = ""

    try:
        # Start streaming with response_format set for JSON
        stream = client.chat.completions.create(
            model="deepseek-chat",  # DeepSeek chat model
            messages=conversation_history,
            response_format={"type": "json_object"},
            stream=True
        )

        console.print("\nAssistant> ", style="bold blue", end="")

        # Process the stream
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content_chunk = chunk.choices[0].delta.content
                full_content += content_chunk
                console.print(content_chunk, end="")

        console.print()  # End the streaming line

        # Parse the complete response
        try:
            parsed_response = json.loads(full_content)
            # Add a default assistant_reply if missing
            if "assistant_reply" not in parsed_response:
                parsed_response["assistant_reply"] = "Processing file changes..."
            
            response_obj = AssistantResponse(**parsed_response)

            # Save the assistant's reply to conversation history
            conversation_history.append({
                "role": "assistant",
                "content": response_obj.assistant_reply
            })

            return response_obj

        except json.JSONDecodeError:
            console.print("[red]✗[/red] Failed to parse JSON response from assistant", style="red")
            return AssistantResponse(
                assistant_reply="Error: Failed to generate valid JSON response.",
                files_to_create=[]
            )

    except Exception as e:
        console.print(f"\n[red]✗[/red] DeepSeek API error: {e}", style="red")
        return AssistantResponse(
            assistant_reply=f"Error: {str(e)}",
            files_to_create=[]
        )

# --------------------------------------------------------------------------------
# 7. Main interactive loop
# --------------------------------------------------------------------------------

def main():
    console.print(Panel.fit(
        "[bold blue]Welcome to Deep Seek Engineer with Structured Output[/bold blue] [green](and streaming)[/green]!🐋",
        border_style="blue"
    ))
    console.print(
        
        
        "To include a file in the conversation, use '[bold magenta]/add path/to/file[/bold magenta]'.\n"
        "Type '[bold red]exit[/bold red]' or '[bold red]quit[/bold red]' to end.\n"
    )

    while True:
        try:
            user_input = console.input("[bold green]You>[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Exiting.[/yellow]")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            console.print("[yellow]Goodbye![/yellow]")
            break

        # If user is reading a file
        if try_handle_add_command(user_input):
            continue

        # Get streaming response from OpenAI
        response_data = stream_openai_response(user_input)

        # Create any files if requested
        if response_data.files_to_create:
            for file_info in response_data.files_to_create:
                create_file(file_info.path, file_info.content)

        # Show and confirm diff edits if requested
        if response_data.files_to_edit:
            show_diff_table(response_data.files_to_edit)
            confirm = console.input("\nDo you want to apply these changes? ([green]y[/green]/[red]n[/red]): ").strip().lower()
            if confirm == 'y':
                for edit_info in response_data.files_to_edit:
                    apply_diff_edit(edit_info.path, edit_info.original_snippet, edit_info.new_snippet)
            else:
                console.print("[yellow]ℹ[/yellow] Skipped applying diff edits.", style="yellow")

    console.print("[blue]Session finished.[/blue]")

if __name__ == "__main__":
    main()