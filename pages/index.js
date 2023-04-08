import Head from "next/head";
import { useState, useEffect } from "react";
import styles from "./index.module.css";

export default function Home() {
  const [questionInput, setQuestionInput] = useState("");
  const [result, setResult] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([{ role: "system", content: "You are a member of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, we have adopted the 1689 London Baptist Confession of Faith that expresses our understanding of the Bible’s vision for the church to promote clarity and transparency at Silicon Valley Reformed Baptist Church." }]);

  async function onSubmit(event) {
    event.preventDefault();
    setIsLoading(true); // Set loading state to true
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: questionInput, conversationHistory }),
      });

      const data = await response.json();
      if (response.status !== 200) {
        throw data.error || new Error(`Request failed with status ${response.status}`);
      }

      // Update conversationHistory
      const newConversationHistory = [
        ...conversationHistory,
        { role: "user", content: questionInput },
        { role: "assistant", content: data.newConversationHistory[data.newConversationHistory.length - 1].content },
      ];
      setConversationHistory(newConversationHistory);
      setQuestionInput("");
      setConversationStarted(true);
    } catch (error) {
      // Consider implementing your own error handling logic here
      console.error(error);
      alert(error.message);
    } finally {
      setIsLoading(false); // Set loading state to false when the request is done or an error occurs
    }
  }

  return (
    <div>
      <Head>
        <title>Calvinist Parrot</title>
        <link rel="icon" href="/calvinist_parrot.ico" />
      </Head>

      <main className={styles.main}>
        <div className={styles.fixedContent}>
          <img src="/calvinist_parrot.gif" className={styles.icon} alt="Calvinist Parrot" />
          <h3>What theological questions do you have?</h3>
        </div>
        <div className={styles.scrollableContent}>
            {conversationStarted &&
              conversationHistory.slice(1).map((message, index) => (
                <p key={index}>
                  <strong>{message.role === "user" ? "Your question" : "Calvinist Parrot"}:</strong> {message.content}
                </p>
              ))}
        </div>
        <div className={styles.formContainer}>
          <form onSubmit={onSubmit}>
            <input
              type="text"
              name="question"
              placeholder="ask a question"
              value={questionInput}
              onChange={(e) => setQuestionInput(e.target.value)}
            />
            <input type="submit" value="Ask" />
            {isLoading && <span>Loading...</span>}
          </form>
        </div>
      </main>


    </div>
  );
}
