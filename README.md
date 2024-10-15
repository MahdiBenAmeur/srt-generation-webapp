# srt-generation-webapp
A web application that enables users to upload both an audio file and a corresponding text script. 
The app transcribes the audio into an SRT (subtitle) file and then synchronizes the transcribed text with the script,
ensuring accurate time codes and alignment between the spoken dialogue and the provided script.

# Setup Instructions
-Backend 
  Install Required Libraries
  Ensure that all necessary libraries listed in the requirements.txt file are installed.
  
  Check CUDA Version
  Verify your CUDA version, then download and install the appropriate PyTorch version. You can find the necessary command on the PyTorch website.
  
  Install FFmpeg 
  
  Download and set up FFmpeg if it’s not installed on your system. FFmpeg is crucial for audio/video processing and handling multimedia files, which many Whisper relies on.

-Frontend
  Set up a Vite React App: Create a new React app using Vite by following the standard setup process.
  Install Additional Packages: react-dropzone ( npm install react-dropzone )



# How It Works
-Initial Transcription
  The audio file is first transcribed using the Whisper large-v2 model, converting the spoken content into an SRT file format.

-Trimming the Audio
  The intro is then trimmed from the audio file, and the corresponding time codes in the SRT file are adjusted.

-Replacing SRT Text with Original Script
  The transcribed text in the SRT file is replaced with the original text from the provided script file, ensuring accuracy.
  
-Splitting Long Subtitles
  If any subtitle surpasses the defined maxNbWords threshold (e.g., 8 words), it is split into smaller subtitles.
  The algorithm ensures the split is logical, creating two parts (e.g., one with 6 words and the other with 3), 
  while avoiding subtitles with only one word to maintain readability.
  
-Optional Punctuation-Based Segment Splitting
  Optionally, we can split the SRT segments further based on punctuation marks. For example:
  
00:00:16,040 --> 00:00:22,500        

   هو دائم المطالعة، غزير المعرفة، طلق اللسان، سريع البديه
                                                                                                                                                                            

can be split into:

5
00:00:16,040 --> 00:00:17,950

هو دائمُ المطالعةِ،

6
00:00:17,950 --> 00:00:19,405

 غزيرُ المعرفةِ،

7
00:00:19,405 --> 00:00:20,860

طلقُ اللّسانٍ،

8
00:00:20,860 --> 00:00:22,406

سَريعُ البديهةِ.
                                                                                                                                                                                                            
While this method provides a more natural flow, it may introduce errors, which we will explain in detail.

# Potential Errors
The updated transcript may encounter errors in certain scenarios:

  # Case 1: Script Contains Extra Phrases Not Present in the Audio
  If the script includes phrases that were not spoken in the audio, we've implemented measures to address this issue. The extra phrases will be appended to the next spoken phrase to maintain the overall coherence   of the transcript.
  
  # Case 2: Audio Contains Additional Speech Not in the Script
  In cases where the audio contains additional dialogue that is not present in the script, we applied a threshold to skip over segments of the audio that don't match the script. However, this threshold may, in      rare cases, cause entire sections of the script to be skipped.

# Advice:
  It is highly recommended to double-check the output SRT file for accuracy before uploading it to the database.

