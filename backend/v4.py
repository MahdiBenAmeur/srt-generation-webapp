import os.path
import re

from datetime import timedelta

import torch
import whisper
from whisper.utils import get_writer

import pysrt

from difflib import SequenceMatcher



MAX_NUMBER_OF_WORDS_IN_SENTANCE=30
THREASHOLD_TO_BE_CHOSEN=60



def format_time(seconds):
    """
    Formats seconds into HH:MM:SS,MMM format for SRT files.
    """
    # Convert seconds to timedelta
    time_str = str(timedelta(seconds=(seconds)))
    #split the time to its parts
    hours, minutes, seconds = time_str.split(':')
    if "." not in seconds:
        seconds+=".000"
    seconds, milliseconds = seconds.split('.')

    # add padding if needed
    hours = hours.zfill(2)
    minutes = minutes.zfill(2)
    seconds = seconds.zfill(2)
    milliseconds = (milliseconds + '00')[:3]  # Ensure milliseconds are exactly 3 digits

    return f"{hours}:{minutes}:{seconds},{milliseconds}"
def remove_diacritics(text):
    # Arabic diacritical marks (Tashkeel)
    arabic_diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652]')

    # Remove diacritics by replacing them with an empty string
    cleaned_text = re.sub(arabic_diacritics, '', text)
    cleaned_text = re.sub(r'[\n\t\r]', ' ', cleaned_text)

    return cleaned_text


def transcribe_audio(path,max_words_per_line=None):
    """
      Transcribes an Arabic audio file using the Whisper large-v2 model and generates an SRT file.
      the srt file is saved in a directory called  SrtFiles

    """
    model_name="large-v2"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)
    model = whisper.load_model(model_name,device=device)

    print(f"finished loading whisper {model_name} model.")

    print("started trasncription...")
    transcribe = model.transcribe(audio=path,word_timestamps=True,language="ar", verbose=False)

    print("generated the transcrition")


    output_directory = "SrtFiles"
    word_options = {
        "highlight_words": False,
        'max_words_per_line':max_words_per_line
    }

    srt_writer = get_writer("srt", output_directory)
    srt_writer(transcribe, path, word_options)



def  matching_scrore(text1,text2):
    """
    calculates the matching scores between too sentences

    :param text1: str the first sentence
    :param text2: str the second sentence
    :return: persentage of the match
    """
    text1=remove_diacritics(text1.replace(" ",""))
    text2=remove_diacritics(text2.replace(" ",""))

    seq_match = SequenceMatcher(None, text1, text2)
    similarity_ratio = seq_match.ratio()
    return similarity_ratio*100


def find_best_match_with_threashold(sub, script: str):
    wordlist = script.split()
    best_match = ""
    best_score = 0

    # Handle case where script contains only one word
    if len(wordlist) <= 2:
        return " ".join(wordlist), 100

    # Compare the first one-word and two-word sentences
    first_word = wordlist[0] + " "
    first_score = matching_scrore(sub, first_word)

    two_words = first_word + wordlist[1] + " "
    second_score = matching_scrore(sub, two_words)

    # Early return if a strong match is found with the first one or two words
    if first_score > 80 and first_score > second_score:
        return wordlist[0], script.find(wordlist[0]) + len(wordlist[0])

    if second_score > 80 and second_score >= first_score:
        return two_words.strip(), script.find(wordlist[1]) + len(wordlist[1])

    # Iterate over longer sentences and find the best match
    last_position = 0
    sentence = two_words
    for i in range(2, min(len(wordlist), MAX_NUMBER_OF_WORDS_IN_SENTANCE)):
        sentence += wordlist[i] + " "
        score = matching_scrore(sub, sentence)
        #print(f"{sentence}, {score}")

        if  score>THREASHOLD_TO_BE_CHOSEN and  score > best_score:
            best_match = sentence.strip()
            best_score = score
            last_position = script.find(wordlist[i]) + len(wordlist[i])

    return best_match, last_position

def find_best_match(sub, script: str):
    """
        Finds the best matching sentence or word sequence from a script that closely matches a provided substring.

        Parameters:
        -----------
        sub : str
            The substring to find a match for in the script.
        script : str
            The rest of script where the matching process is performed.

        Returns:
        --------
        tuple : (str, int)
            A tuple containing:
            - The best matching word sequence from the script (str).
            - The position (index) in the script after the best matching sequence (int).
    """

    wordlist = script.split()
    best_match = ""
    best_score = 0

    # Handle case where script contains only one word
    if len(wordlist) <= 2:
        return " ".join(wordlist), 100

    # Compare the first one-word and two-word sentences
    first_word = wordlist[0] + " "
    first_score = matching_scrore(sub, first_word)

    two_words = first_word + wordlist[1] + " "
    second_score = matching_scrore(sub, two_words)

    # Early return if a strong match is found with the first one or two words
    if first_score > 90 and first_score > second_score:
        return wordlist[0], script.find(wordlist[0]) + len(wordlist[0])

    if second_score > 90 and second_score >= first_score:
        return two_words.strip(), script.find(wordlist[1]) + len(wordlist[1])

    # Iterate over longer sentences and find the best match
    last_position = 0
    sentence = two_words
    for i in range(2, min(len(wordlist), MAX_NUMBER_OF_WORDS_IN_SENTANCE)):
        sentence += wordlist[i] + " "
        score = matching_scrore(sub, sentence)
        #print(f"{sentence}, {score}")

        if   score> 35 and score > best_score:
            best_match = sentence.strip()
            best_score = score
            last_position = script.find(wordlist[i]) + len(wordlist[i])
    #print(best_score)
    return best_match, last_position

def trim_intro(srt_file,script_path):
    """
    removes the intro from the srt file

    :param srt_file: path to the srt file
    :param script_path: path to the script file
    :return: nothing updates happen to the original srt file
    """
    with open(script_path,"r",encoding="utf-8") as sf:
        script=sf.read()


    subs=pysrt.open(srt_file)
    for index, sub in enumerate(subs):
        if index==3:
            break
        best,acc=find_best_match_with_threashold(sub.text,script[:])
        if best!="":
            break
        sub.text=""
    subs.save(srt_file)


def srt_time_to_seconds(srt_time):
    srt_time=str(srt_time)
    # Split hours, minutes, and seconds+milliseconds
    hours, minutes, seconds_millis = srt_time.split(':')

    # Split seconds and milliseconds
    seconds, millis = seconds_millis.split(',')

    # Convert to total seconds
    total_seconds = (int(hours) * 3600) + (int(minutes) * 60) + int(seconds) + (int(millis) / 1000)

    return total_seconds
def cut_srt_by_ponctuation(srt_path):
    """
       Splits SRT subtitles into smaller segments based on punctuation (., ، ؛ ؟ !).

       This function reads an SRT file, splits subtitle entries where punctuation is found, and creates
       new subtitle entries for each segment. It maintains the original timing structure by distributing
       the duration proportionally across the newly created subtitle segments.

       Parameters:
       -----------
       srt_path : str
           The path to the SRT file that needs to be split.
    """
    subtiles=pysrt.open(srt_path,encoding="utf-8")
    new_subtitles = pysrt.SubRipFile()

    for subtile in subtiles:
        list_subtile = re.findall(r'[^.,،؛؟!]+[.,،؛؟!]*', subtile.text)
        if len(list_subtile)>1:
            print("------------------------------------------------------------------------------")
            print(list_subtile)
            starting_time=subtile.start
            ending_time=subtile.end
            duration=srt_time_to_seconds(ending_time)-srt_time_to_seconds(starting_time)
            for section in list_subtile:
                if section.replace(" ","")=="":
                    continue
                section_duration= (len(section)/len(subtile.text))*duration
                # Create a new subtitle entry
                new_subtitle = pysrt.SubRipItem()

                new_subtitle.start = pysrt.SubRipTime.from_string(str(starting_time))
                starting_time = format_time(srt_time_to_seconds(starting_time)+section_duration)
                new_subtitle.end = pysrt.SubRipTime.from_string(str(starting_time))

                new_subtitle.text = section # Set the text of the section

                new_subtitles.append(new_subtitle)

        else:
            new_subtitles.append(subtile)
    for index,sub in enumerate(new_subtitles,start=1):
        sub.index=index

    new_subtitles.save(srt_path, encoding="utf-8")






def update_srt_file(srt_path,script_path):
    """
    replaces the text in the srt by its matching text in the script
    :param srt_path:  str
    :param script_path: str
    :return: str : path for the result
    """

    with open(script_path,"r", encoding='utf-8') as scriptfile:
        script=scriptfile.read()
    scriptfile.close()

    script=script.replace('n', " ")
    script=script.replace('r', " ")
    script=script.replace('\\', " ")
    script=script.replace('"', " ")
    script=script.replace('-', " ")





    #script= re.sub(r'[\n\t\r]', ' ', script)
    # Load the SRT file
    subs = pysrt.open(srt_path,encoding='utf-8')

    # Create a list of subtitles starting after 4 seconds
    position=0

    for index,sub in enumerate(subs):
        if position>len(script):
            break
        if sub.text=="":
            continue
        print("-----------------------------------------------------------------------")
        #print(f"srt sub : {sub.text} \n whats written :{script[position:position+100]}")

        best_match,accrument=find_best_match(sub.text,script[position:])
        position+=accrument
        print(f"srt sub : {sub.text}")
        print(f"best match : {best_match}")
        sub.text=best_match
    resultpath=srt_path[:-4]+"_result.srt"
    for i,sub in enumerate(subs):
        if i <index:
            continue
        sub.text=""

    subs.save(resultpath)
    return resultpath



def check_correctness(srt_path,script_path):
    with open(script_path, "r", encoding='utf-8') as scriptfile:
        script = scriptfile.read()
    script=remove_diacritics(script)
    scriptfile.close()

    print(script)
    subs=pysrt.open(srt_path,encoding='utf-8')
    for sub in subs:
        pos=script.find(remove_diacritics(sub.text))
        if pos!=-1:
            print(f"{sub.text} is in {pos}")
        else:
            print(f"{sub.text} does not exist")



def transcribe_and_correct(audio_path,text_path,max_words_per_line=None, cut_by_punctuation=False ):
    srt_directory = "SrtFiles"
    srt_name = os.path.basename(audio_path)[:-4] + ".srt"

    #get transcribte
    transcribe_audio(audio_path) #resulting srt will be stored in SrtFiles Directory under the same name as the audio


    #result path
    srt_path=os.path.join(srt_directory, srt_name)

    #trim the intro "حكايات كلاس كويز"

    trim_intro(srt_path,text_path)

    #update the srt file with the real text

    result_path=update_srt_file(srt_path,text_path)

    if max_words_per_line:
        cut_by_max_nb_words(result_path,maxnbwords=8)



    #cut srt file by punctiation

    if cut_by_punctuation:
        cut_srt_by_ponctuation(srt_path)

    return result_path


def cut_by_max_nb_words(srt_path,maxnbwords):
    subs=pysrt.open(srt_path,encoding='utf-8')
    new_subs=pysrt.SubRipFile()

    for sub in subs:
        words=sub.text.split()
        starting_time=sub.start
        ending_time=sub.end
        duration=srt_time_to_seconds(ending_time)-srt_time_to_seconds(starting_time)
        while len(words)>maxnbwords:
            new_words=words[:int(maxnbwords*0.7)]
            new_sentence=" ".join(new_words)
            section_duration= (len(new_sentence)/len(sub.text))*duration


            new_subtitle = pysrt.SubRipItem()



            new_subtitle.start = pysrt.SubRipTime.from_string(str(starting_time))
            ending_time = format_time(srt_time_to_seconds(starting_time)+section_duration)
            new_subtitle.end = pysrt.SubRipTime.from_string(str(ending_time))

            new_subtitle.text = new_sentence # Set the text of the section
            new_subs.append(new_subtitle)
            starting_time=ending_time

            words=words[int(maxnbwords*0.7):]
        if words:
            new_sentence=" ".join(words)
            section_duration= (len(new_sentence)/len(sub.text))*duration


            new_subtitle = pysrt.SubRipItem()



            new_subtitle.start = pysrt.SubRipTime.from_string(str(starting_time))
            ending_time = format_time(srt_time_to_seconds(starting_time)+section_duration)
            new_subtitle.end = pysrt.SubRipTime.from_string(str(ending_time))

            new_subtitle.text = new_sentence # Set the text of the section
            new_subs.append(new_subtitle)


    for index,sub in enumerate(new_subs,start=1):
        sub.index=index
    new_subs.save(srt_path)







if __name__=="__main__":
    audio_path="input_audio\\fifth_story.mp3"
    script_path="input_text/story5.txt"
    #transcribe_and_correct(audio_path,script_path,max_words_per_line=8)
    #update_srt_file("SrtFiles\\forth_story.srt","input_text\story4.txt")
    #cut_by_max_nb_words("SrtFiles\\forth_story_result.srt",8)
    """
    cut_srt_by_ponctuation("SrtFiles/first_story_result.srt")

    #transcribe_and_correct(audio_path,script_path)
    #transcribe_audio("input_audio/first_story.mp3")
    srtpath="SrtFiles/second_story.srt"
    script_path="input_text/story2.txt"
    trim_intro(srtpath,script_path)
    result_path=update_srt_file(srtpath,script_path)
    cut_srt_by_ponctuation(result_path)"""

    """
    #check(srtpath,script_path)"""


