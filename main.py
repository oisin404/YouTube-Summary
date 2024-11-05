import openai
from pytube import YouTube

def loadConfig():
    import json
    with open('config.json', 'r') as f:
        return json.load(f)

def fetchCaptions(url):
    try:
        print(f"Fetching captions for video: {url}")
        yt = YouTube(url)

        # Print available captions for debugging
        print("Available captions:")
        for lang in yt.captions:
            print(f"- {lang}: {yt.captions[lang].name}")

        captionText = None

        # Attempt to fetch English or auto-generated captions
        if 'en' in yt.captions:
            print("Fetching standard English captions...")
            captionText = yt.captions['en'].generate_srt_captions()
        elif 'a.en' in yt.captions:
            print("Fetching auto-generated English captions...")
            captionText = yt.captions['a.en'].generate_srt_captions()
        else:
            print("No standard or auto-generated English captions available.")

        if captionText:
            print("Captions fetched successfully.")
            return captionText

        print("No English captions available.")
        return None
    except Exception as e:
        print(f"Error fetching captions: {e}")
        return None

def cleanCaptions(captions):
    # Remove SRT formatting and return plain text
    import re
    cleanedText = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', captions)
    cleanedText = re.sub(r'\n+', ' ', cleanedText).strip()
    return cleanedText

def summarizeWithOpenAI(text):
    config = loadConfig()
    openai.api_key = config["apikey"]

    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Summarize the following text:\n\n{text}",
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        summary = response.choices[0].text.strip()
        return summary
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None

def main():
    config = loadConfig()
    videoUrl = config.get("videoUrl")

    if not videoUrl:
        print("Video URL not found in config.")
        return

    captions = fetchCaptions(videoUrl)

    if captions:
        cleanedText = cleanCaptions(captions)
        summary = summarizeWithOpenAI(cleanedText)

        if summary:
            print("Summary:", summary)
        else:
            print("No summary was generated.")
    else:
        print("No captions were fetched.")

if __name__ == "__main__":
    main()