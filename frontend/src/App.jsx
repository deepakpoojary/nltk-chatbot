import React, { useState } from "react";
import axios from "axios";
import "./App.css"; // We'll move the CSS into a separate file
import html2pdf from "html2pdf.js"; // Import html2pdf.js

const App = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!userInput) return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "User", text: userInput },
    ]);
    setUserInput("");
    setIsLoading(true);
    try {
      const response = await axios.post(
        "/chat",
        { message: userInput },
        {
          headers: { "Content-Type": "application/json" },
        }
      );

      const data = response.data;
      const chatResponse =
        data.response?.getTestForPortal?.[0]?.html || data.response;

      setMessages((prevMessages) => [
        ...prevMessages,
        {
          sender: "Bot",
          text: chatResponse,
          isHtml: !!data.response?.getTestForPortal?.[0]?.html,
        },
      ]);
    } catch (error) {
      console.error("Error fetching chat response:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  const handleDownload = () => {
    setIsLoading(true); // Show loading symbol while downloading

    const htmlMessages = messages.filter((message) => message.isHtml);
    const htmlMessage = htmlMessages[htmlMessages.length - 1];
    if (htmlMessage) {
      const element = document.createElement("div");
      element.innerHTML = htmlMessage.text;
      element.style.width = "7.5in"; // Set width to standard US letter size
      element.style.height = "10in";

      const opt = {
        margin: 0.5,
        filename: "html_content.pdf",
        image: { type: "jpeg", quality: 1 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      };

      html2pdf()
        .from(element)
        .set(opt)
        .save()
        .then(() => {
          setIsLoading(false); // Hide loading symbol after download completes
        });
    }
  };
  const getScaleFactor = () => {
    return Math.min(window.innerWidth / 794 - 0.021, 1);
  };
  return (
    <div id="chatbox">
      <header>Chatbot</header>
      <div id="chatlog">
        {messages.map((message, index) => (
          <p key={index}>
            <strong>{message.sender}:</strong>
            <span className="message-space"></span>
            {message.isHtml ? (
              <>
                <div
                  className="html-frame"
                  style={{
                    transform: `scale(${getScaleFactor()})`,
                    transformOrigin: "top left",
                  }}
                >
                  <span dangerouslySetInnerHTML={{ __html: message.text }} />
                </div>
                <button className="thisbutton" onClick={handleDownload}>
                  Download PDF
                </button>
              </>
            ) : (
              message.text
            )}
          </p>
        ))}
        {isLoading && (
          <p>
            <strong>Bot:</strong> Loading...
          </p>
        )}
      </div>
      <input
        type="text"
        id="userInput"
        placeholder="Type your message here"
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        onKeyDown={handleKeyPress}
      />
      <button className="thisbutton" onClick={sendMessage}>
        Send
      </button>

      {/* {!isLoading && (
        <button className="thisbutton" onClick={fetchHtmlContent}>
          Fetch HTML Content
        </button>
      )} */}
    </div>
  );
};

export default App;
