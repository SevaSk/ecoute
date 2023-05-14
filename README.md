
# 🎧 Ecoute

Ecoute is a live transcription tool that provides real-time transcripts for both the user's microphone input (You) and the user's speakers output (Speaker) in a textbox. It also generates a suggested response using OpenAI's GPT-3.5 for the user to say based on the live transcription of the conversation.

## 📖 Description

**Ecoute** is designed to help users in their conversations by providing live transcriptions and generating contextually relevant responses. By leveraging the power of OpenAI's GPT-3.5, Ecoute aims to make communication more efficient and enjoyable.

## 🚀 Getting Started

Follow these steps to set up and run ecoute on your local machine.

### 📋 Prerequisites

- Python 3.x
- An OpenAI API key
- Windows OS (Haven't tested on others)

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
   
4. Create a `keys.py` file and add your OpenAI API key:

   ```
   echo 'OPENAI_API_KEY = "API KEY"' > keys.py
   ```

   Replace `API KEY` with your actual OpenAI API key.

### 🎬 Running ecoute

Run the main script:

```
python main.py
```

Now, ecoute will start transcribing your microphone input and speaker output in real-time, and provide a suggested response based on the conversation. It may take a couple seconds for it to warm up before the transcription becomes real time.

## 📖 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve ecoute.
