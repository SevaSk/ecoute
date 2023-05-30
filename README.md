
# 🎧 Ecoute

Ecoute is a live transcription tool that provides real-time transcripts for both the user's microphone input (You) and the user's speakers output (Speaker) in a textbox. It also generates a suggested response using OpenAI's GPT-3.5 for the user to say based on the live transcription of the conversation.

## 📖 Demo

https://github.com/SevaSk/ecoute/assets/50382291/8ac48927-8a26-49fd-80e9-48f980986208

Ecoute is designed to help users in their conversations by providing live transcriptions and generating contextually relevant responses. By leveraging the power of OpenAI's GPT-3.5, Ecoute aims to make communication more efficient and enjoyable.

## 🚀 Getting Started

Follow these steps to set up and run Ecoute on your local machine.

### 📋 Prerequisites

- Python 3.x
- An OpenAI API key
- Windows OS (Not tested on others)
- FFmpeg 

If FFmpeg is not installed in your system, you can follow the steps below to install it.

First, you need to install Chocolatey, a package manager for Windows. Open your PowerShell as Administrator and run the following command:
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
Once Chocolatey is installed, you can install FFmpeg by running the following command in your PowerShell:
```
choco install ffmpeg-full
```
Please ensure that you run these commands in a PowerShell window with administrator privileges. If you face any issues during the installation, you can visit the official Chocolatey and FFmpeg websites for troubleshooting.

To run on mac os, please install the following
`brew install portaudio`
`brew install python-tk `

### 🔧 Installation

1. Clone the repository:

   ```
   git clone https://github.com/SevaSk/ecoute
   ```

2. Navigate to the `ecoute` folder:

   ```
   cd ecoute
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```
   
4. Create a `keys.py` file in the ecoute directory and add your OpenAI API key:

   ```
   python -c "with open('keys.py', 'w', encoding='utf-8') as f: f.write('OPENAI_API_KEY=\"API KEY\"')"
   ```

   Replace `API KEY` with your actual OpenAI API key.


### 🎬 Running Ecoute

Run the main script:

```
python main.py
```

For a better and faster version, use:

```
python main.py --api
```

Upon initiation, Ecoute will begin transcribing your microphone input and speaker output in real-time, generating a suggested response based on the conversation. Please note that it might take a few seconds for the system to warm up before the transcription becomes real-time.

The --api flag significantly enhances transcription speed and accuracy, and it's expected to be the default option in future releases. However, keep in mind that using the Whisper API will consume more OpenAI credits than using the local model. This increased cost is attributed to the advanced features and capabilities that the Whisper API provides. Despite the additional cost, the considerable improvements in speed and transcription accuracy might make it a worthwhile investment for your use case.

### ⚠️ Limitations

While Ecoute provides real-time transcription and response suggestions, there are several known limitations to its functionality that you should be aware of:

**Default Mic and Speaker:** Ecoute is currently configured to listen only to the default microphone and speaker set in your system. It will not detect sound from other devices or systems. If you wish to use a different mic or speaker, you will need to set it as your default device in your system settings.

**Whisper Model**: If the --api flag is not used, we utilize the 'tiny' version of the Whisper ASR model, due to its low resource consumption and fast response times. However, this model may not be as accurate as the larger models in transcribing certain types of speech, including accents or uncommon words.

**Language**: The Whisper model used in Ecoute is set to English. As a result, it may not accurately transcribe non-English languages or dialects. We are actively working to add multi-language support to future versions of the program.

## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve Ecoute.
