import React, { useState } from "react";
import axios from "axios";
import "./PdfSummarizer.css";
import "@react-pdf-viewer/core/lib/styles/index.css";

const PdfSummarizer = () => {
  const [file, setFile] = useState(null);
  const [fileUrl, setFileUrl] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
      setFile(file);
      setFileUrl(URL.createObjectURL(file));
    } else {
      alert("Please upload a valid PDF file.");
    }
  };

  const summarizeText = async () => {
    if (!file || !fileUrl) {
      alert("Please select a PDF file.");
      return;
    }
  
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/summarize",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
  
      setSummary(response.data[0].summary);
      console.log(response.data[0]);
    } catch (error) {
      console.error("Error summarizing the PDF:", error);
      setSummary("Failed to summarize the PDF.");
    } finally {
      setLoading(false);
    }
    setLoading(false);
  };

  return (
    <div className="container">
      <h1>PDF Summarizer</h1>
      <input type="file" onChange={handleFileChange} />

      {fileUrl && (
        <div>
          <iframe
            src={fileUrl}
            width="100%"
            height="500px"
            style={{ marginBottom: "20px" }}
          />
        </div>
      )}

      {loading && <p>Summarizing...</p>}

      <button className="button" onClick={summarizeText} disabled={!file}>
        Summarize
      </button>

      {summary && (
        <div className="summary">
          <h3>Summarized Content:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
};

export default PdfSummarizer;
