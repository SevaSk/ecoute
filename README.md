
# 👂🏻️ Transcribe ✍🏼️

Transcribe is a live transcription tool that provides real-time transcripts for the microphone input (You) and the audio output (Speaker). It optionally generates a suggested response using OpenAI's GPT-3.5 for the user to say based on the live transcription of the conversation.

## 🆕 Getting Started 🥇

Follow below steps to run transcribe on your local machine.

### 📋 Prerequisites

- Python >=3.8.0
- (Optional) An OpenAI API key that can access OpenAI API (set up a paid account OpenAI account)
- Windows OS (Not tested on others)
- FFmpeg 

If FFmpeg is not installed in your system, follow the steps below to install it.

First, install Chocolatey, a package manager for Windows. Open PowerShell as Administrator and run the following command:
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Once Chocolatey is installed, install FFmpeg by running the following command in your PowerShell:
```
choco install ffmpeg
```
Please run these commands in a PowerShell window with administrator privileges. For any issues during the installation, visit the official [Chocolatey](https://chocolatey.org/) and [FFmpeg](https://ffmpeg.org/) websites for troubleshooting.

### 🔧 Code Installation

1. Clone transcribe repository:

   ```
   git clone https://github.com/vivekuppal/transcribe
   ```

2. Navigate to the `transcribe` folder:

   ```
   cd transcribe
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```
   
4. (Optional) Replace the Open API key in `parameters.yaml` file in the transcribe directory:

   Replace the Open API key in `parameters.yaml` file manually. Open in a text editor and alter the line:
   
      ```
        api_key: 'API_KEY'
      ```
      Replace "API KEY" with the actual OpenAI API key. Save the file.

### 🎬 Running Transcribe

Run the main script:

```
python main.py
```

For a better and faster version that also works with most languages, use:

```
python main.py --api
```

Upon initiation, Transcribe will begin transcribing microphone input and speaker output in real-time, optionally generating a suggested response based on the conversation. It might take a few seconds for the system to warm up before the transcription becomes real-time.

The --api flag will use the whisper api for transcriptions. This significantly enhances transcription speed and accuracy, and it works in most languages (rather than just English without the flag). However, keep in mind, using the Whisper API consumes OpenAI credits than using the local model. This increased cost is attributed to the advanced features and capabilities that the Whisper API provides. Despite the additional expense, the substantial improvements in speed and transcription accuracy may make it a worthwhile for your use case.

### Crating Windows installs

Install Winrar from https://www.win-rar.com/.

Required for generating binaries from python code. If you do not intend to generate binaries and are only writing python code, you do not need to install winrar. 

In the file ```generate_binary.bat``` replace these paths at the top of the file to paths specific to your machine. 

```
SET SOURCE_DIR=D:\Code\transcribe  
SET OUTPUT_DIR=D:\Code\transcribe\output
SET LIBSITE_PACAGES_DIR=D:\Code\transcribe\venv\Lib\site-packages
SET EXECUTABLE_NAME=transcribe.exe
SET ZIP_FILE_DIR=D:\Code\transcribe\transcribe.rar
SET WINRAR=C:\Program Files\WinRAR\winRAR.exe
```

Run ```generate_binary.bat``` file by replacing paths at the top of the file to the ones in your local machine. It should generate a zip file with everything compiled. To run the program simply go to zip file > transcribe.exe.

## Software Installation

1. Download the zip file from
```
https://drive.google.com/file/d/1UJR4rJt5umxxOiAHNGXPMhnnYr6Bj6fX/view?usp=sharing
```
2. Unzip the files in a folder.

3. (Optional) Replace the Open API key in `parameters.yaml` file in the transcribe directory:

   Replace the Open API key in `parameters.yaml` file manually. Open in a text editor and alter the line:

      ```
        api_key: 'API_KEY'
      ```
      Replace "API KEY" with the actual OpenAI API key. Save the file.

4. Execute the file `transcribe\transcribe.exe\transcribe.exe`


### ⚡️ Limitations ⚡️

While Transcribe provides real-time transcription and optional response suggestions, there are several known limitations to its functionality that you should be aware of:

**Default Mic and Speaker:** Transcribe is currently configured to listen only to the default microphone and speaker set in your system. It will not detect sound from other devices or systems. To use a different mic or speaker, need to set it as your default device in your system settings.

**Whisper Model**: If the --api flag is not used, we utilize the 'tiny' version of the Whisper ASR model, due to its low resource consumption and fast response times. However, this model may not be as accurate as the larger models in transcribing certain types of speech, including accents or uncommon words.

**OpenAI Account**: If a paid OpenAI account with a valid Open API Key is not used, the command window displays the following error message repeatedly, though the application behvaior is not impacted in any way.
```
Incorrect API key provided: API_KEY. You can find your API key at https://platform.openai.com/account/api-keys.
```

**Models**: The default install of transcribe has the tiny(72 Mb) model. base (138 Mb), small (461 Mb) models can be downloaded and used for transcription by following instructions using transcribe command line. The larger models provide better quality transcription and they have higher memory requirements.

**Language**: If you are not using the --api flag the Whisper model used in Transcribe is set to English. As a result, it may not accurately transcribe non-English languages or dialects. 

## 👤 License 📖

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ➕ Enhancements from base repository ➕
- Do not need Open AI key, paid Open AI account to use the complete functionality
- Allow users to add contextual information to provide customized responses to conversation
- Allows usage of different models for transcription using command line arguments
- Allow to pause audio transcription
- Transcribe audio of any video
- Preserve all conversation text in UI
- Allow saving conversation to file


## 🤝 Contributing 🤝

Contributions are welcome! Feel free to open issues or submit pull requests to improve Transcribe.
