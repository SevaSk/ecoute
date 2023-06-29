
# 🎧 Ecoute

Transcribe is a live transcription tool that provides real-time transcripts for the microphone input (You) and the speakers output (Speaker). It optionally generates a suggested response using OpenAI's GPT-3.5 for the user to say based on the live transcription of the conversation.

## 📖 Demo

Transcribe is designed to help users in their conversations by providing live transcriptions and generating contextually relevant responses. By leveraging the power of OpenAI's GPT-3.5, Transcribe aims to make communication more efficient and enjoyable.

## 🚀 Getting Started

Follow these steps to set up and run transcribe on your local machine.

### 📋 Prerequisites

- Python >=3.8.0
- An OpenAI API key that can access OpenAI API (set up a paid account OpenAI account, required only if you desire it to prompt for suggested responses.)
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
Please ensure that you run these commands in a PowerShell window with administrator privileges. For any issues during the installation, visit the official Chocolatey and FFmpeg websites for troubleshooting.

### 🔧 Installation

1. Clone the repository:

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
   
4. (Optional) Create a `keys.py` file in the transcribe directory and add OpenAI API key:

   - Option 1: Use command prompt. Run the following command, ensuring to replace "API KEY" with the actual OpenAI API key:

      ```
      python -c "with open('keys.py', 'w', encoding='utf-8') as f: f.write('OPENAI_API_KEY=\"API KEY\"')"
      ```

   - Option 2: Create the keys.py file manually. Open a text editor and enter the following content:
   
      ```
      OPENAI_API_KEY="API KEY"
      ```
      Replace "API KEY" with the actual OpenAI API key. Save this file as keys.py within the transcribe directory.

### 🎬 Running Transcribe

Run the main script:

```
python main.py
```

For a more better and faster version that also works with most languages, use:

```
python main.py --api
```

Upon initiation, Transcribe will begin transcribing microphone input and speaker output in real-time, optionally generating a suggested response based on the conversation. It might take a few seconds for the system to warm up before the transcription becomes real-time.

The --api flag will use the whisper api for transcriptions. This significantly enhances transcription speed and accuracy, and it works in most languages (rather than just English without the flag). However, keep in mind that using the Whisper API consumes more OpenAI credits than using the local model. This increased cost is attributed to the advanced features and capabilities that the Whisper API provides. Despite the additional expense, the substantial improvements in speed and transcription accuracy may make it a worthwhile for your use case.

### ⚠️ Limitations

While Transcribe provides real-time transcription and response suggestions, there are several known limitations to its functionality that you should be aware of:

**Default Mic and Speaker:** Transcribe is currently configured to listen only to the default microphone and speaker set in your system. It will not detect sound from other devices or systems. To use a different mic or speaker, need to set it as your default device in your system settings.

**Whisper Model**: If the --api flag is not used, we utilize the 'tiny' version of the Whisper ASR model, due to its low resource consumption and fast response times. However, this model may not be as accurate as the larger models in transcribing certain types of speech, including accents or uncommon words.

**Language**: If you are not using the --api flag the Whisper model used in Ecoute is set to English. As a result, it may not accurately transcribe non-English languages or dialects. 

## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve Transcribe.
