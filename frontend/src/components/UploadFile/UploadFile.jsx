import React, { useState,useEffect } from "react";
import Dropzone from "react-dropzone";
import "./Dropzone.css";
import Element from "./Element";

const UploadFile = () => {
  const [listfile, setlistFile] = useState([]);
  const [downloadlink, setdownloadlink] = useState(null);
  const [converting,setconverting] = useState(false);
  const [buttonName, setButtonName] = useState("Converting...");
  const [maxNbWords, setmaxNbWords] = useState(8);
    const handleChange = (event) => {
    setmaxNbWords(event.target.value);
    };

  useEffect(() => {
    if (downloadlink) {
      setButtonName("Click to Download");
    } else {
      setButtonName("Converting...");
    }
  }, [downloadlink]);
const handledownload = async () => {
  if (!downloadlink) {
    alert("No transcript available yet!");
    return;
  } else {
    try {
      const api = "http://127.0.0.1:8000/download";
      const formdata=new FormData();
      formdata.append("path",downloadlink);
      const response = await fetch(api, {
        method: "POST",
        body: formdata,
        headers: {
          Accept: "application/octet-stream",
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "transcript.srt";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);

        // Reset state variables to their initial values
        setlistFile([]);
        setdownloadlink(null);
        setconverting(false);
        setButtonName("Converting...");
      } else {
        alert("Failed to download transcript!");
      }
    } catch (error) {
      console.error("Error during download:", error);
      alert("An error occurred while downloading the transcript!");
    }
  }
};


  
  const handleConvert = async () => {

    console.log("clicked");

    const url = "http://127.0.0.1:8000/convert";
    const formData = new FormData();

    const toUpload = Array.from(listfile); // Ensure you are appending multiple files correctly

    // Append each file under the "files" key (you can append multiple times with the same key)
    toUpload.forEach(file => {
        formData.append("files", file); // Appending all files with the same key
    });

    formData.append("maxnbwords", maxNbWords); // Append maxNbWords correctly

  for (let [key, value] of formData.entries()) {
    console.log(key, value);
  }

    console.log("trying to upload")
    setlistFile([])
    setconverting(true);
    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      });

      if (response.ok) {

        const data = await response.json();
        console.log("Server Response: ", data);
        setdownloadlink(data.download_url);

      } else {
        console.error("File upload failed", response.status);
      }
    } catch (error) {
      console.error("Error uploading files:", error);
    }
  };

  const handleUpload = (acceptedFiles) => {
    console.log("logging drop/selected file", acceptedFiles);

    const updatedList = [...acceptedFiles, ...listfile];
    console.log("logging drop/list of file", updatedList);

    let firstAudioFile = null;
    let firstTextFile = null;

    updatedList.forEach((file) => {
      if (file.type === "audio/mpeg" && !firstAudioFile) {
        firstAudioFile = file; // First audio file
      } else if (file.type === "text/plain" && !firstTextFile) {
        firstTextFile = file; // First text file
      }
    });

    const newList = [];
    if (firstAudioFile) newList.push(firstAudioFile);
    if (firstTextFile) newList.push(firstTextFile);

    setlistFile(newList);
    console.log("updated list ", newList);
  };

  return (
    <div className="dropzone-container">
      <Dropzone
        onDrop={handleUpload}
        accept={{
          "audio/mpeg": [".mp3"],
          "text/plain": [".txt"],
        }}
        disabled={converting}
      >
        {({
          getRootProps,
          getInputProps,
          isDragActive,
          isDragAccept,
          isDragReject,
        }) => {
          const additionalClass = isDragAccept
            ? "accept"
            : isDragReject
            ? "reject"
            : "";

          return (
            <div
              {...getRootProps({
                className: `dropzone ${additionalClass}`,
              })}
            >
              <input {...getInputProps()} />
              <p>Drag and drop the input, or click to select files</p>
            </div>
          );
        }}
      </Dropzone>
      {listfile.length > 0 && (
        <>
          {listfile.map((file, index) => (
            <div key={index}>
              <Element file={file} />
              <br />
            </div>
          ))}
        </>
      )}
      {listfile.length === 2 && (
        <div className="butttoncontainer">
          <button className="button-27" onClick={handleConvert}>
            Convert
          </button>
          <div className="inputcontainer">
            <p>
              max number of words
            </p>
            <input
            className="input-max"
              type="number"
              min="1"
              max="1000"
              value={maxNbWords}
              onChange={handleChange}
            ></input>
          </div>
        </div>
      )}
      {converting && (
        <div className="butttoncontainer">
          <button
            className="button-27-converting"
            onClick={handledownload}
            disabled={buttonName === "Converting..."}
          >
            {buttonName}
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadFile;
