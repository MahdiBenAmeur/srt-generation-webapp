
import "./Element.css"
import mp3Icon from "../../icons/mp3.png"
import txtIcon from "../../icons/txt.png"
function Element({ file }) {
  const getIcon = (fileType) => {
    if (fileType === "audio/mpeg") {
      return mp3Icon; // Replace with actual URL of MP3 icon
    } else if (fileType === "text/plain") {
      return txtIcon; // Replace with actual URL of TXT icon
    }
    return "DEFAULT_ICON_URL"; // Optional: Default icon
  };

  return (
    <div className="element_container">
      <img className="elementIcon" src={getIcon(file.type)} alt={`${file.name} icon`} />
      <h3>{file.name}</h3>
    </div>
  );
}

export default Element;