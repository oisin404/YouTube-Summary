import re
from pytube import YouTube
import openai
import json


def loadConfig():
    try:
        with open('config.json') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from config file.")
        return {}


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
            captionText = yt.captions['en'].generate_srt_captions()
        elif 'a.en' in yt.captions:
            captionText = yt.captions['a.en'].generate_srt_captions()
        else:
            print("No standard or auto-generated English captions available.")

        if captionText:
            return captionText

        print("No English captions available.")
        return None
    except Exception as e:
        print(f"Error fetching captions: {e}")
        return None


def cleanCaptions(captionText):
    print("Cleaning captions...")
    cleanedText = re.sub(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}", "", captionText)
    cleanedText = re.sub(r"\n\d+\n", "\n", cleanedText)
    cleanedText = re.sub(r"\n+", " ", cleanedText).strip()
    return cleanedText


def summarizeWithOpenAI(cleanedText):
    api_key = loadConfig().get("apikey")

    if not api_key:
        print("API key not found.")
        return None

    openai.api_key = api_key

    print("Summarizing text with OpenAI...")
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Please summarize the following text: {cleanedText}"}
            ],
        )
        return completion.choices[0].message.content

    except Exception as e:
        print("Error communicating with OpenAI:", e)
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
