# Deep Seek Engineer 🐋

## Overview

This repository contains a powerful coding assistant application that integrates with the DeepSeek API to process user conversations and generate structured JSON responses. Through an intuitive command-line interface, it can read local file contents, create new files, and apply diff edits to existing files in real time.

## Key Features

1. DeepSeek Client Configuration
   - Automatically configures an API client to use the DeepSeek service with a valid DEEPSEEK_API_KEY. 
   - Connects to the DeepSeek endpoint specified in the environment variable to stream GPT-like completions. 

2. Data Models
   - Leverages Pydantic for type-safe handling of file operations, including:
     • FileToCreate – describes files to be created or updated.  
     • FileToEdit – describes specific snippet replacements in an existing file.  
     • AssistantResponse – structures chat responses and potential file operations.  

3. System Prompt
   - A comprehensive system prompt (system_PROMPT) guides conversation, ensuring all replies strictly adhere to JSON output with optional file creations or edits.  

4. Helper Functions
   - read_local_file: Reads a target filesystem path and returns its content as a string.  
   - create_file: Creates or overwrites a file with provided content.  
   - show_diff_table: Presents proposed file changes in a rich, multi-line table.  
   - apply_diff_edit: Applies snippet-level modifications to existing files.  

5. “/add” Command
   - Users can type “/add path/to/file” to quickly read a file’s content and insert it into the conversation as a system message.  
   - This allows the assistant to reference the file contents for further discussion, code generation, or diff proposals.  

6. Conversation Flow
   - Maintains a conversation_history list to track messages between user and assistant.  
   - Streams the assistant’s replies via the DeepSeek API, parsing them as JSON to preserve both the textual response and the instructions for file modifications.  

7. Interactive Session
   - Run the script (for example: “python3 main.py”) to start an interactive loop at your terminal.  
   - Enter your requests or code questions. Enter “/add path/to/file” to add file contents to the conversation.  
   - When the assistant suggests new or edited files, you can confirm changes directly in your local environment.  
   - Type “exit” or “quit” to end the session.  

## Getting Started

1. Prepare a .env file with your DeepSeek API key:
   DEEPSEEK_API_KEY=your_api_key_here

2. Install the required dependencies:
   pip install -r requirements.txt

3. Launch the coding assistant:
   python3 main.py

4. Enjoy multi-line streaming responses, file read-ins with “/add path/to/file”, and precise file edits when approved.

