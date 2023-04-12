import Head from "next/head";
import { useState, useEffect } from "react";
import styles from "./index.module.css";

export default function Home() {
  const [questionInput, setQuestionInput] = useState("");
  const [result, setResult] = useState();
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [conversationHistory_parrot, setConversationHistory_parrot] = useState([{
    role: "system", content: "You are a member of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, we have adopted the 1689 London Baptist Confession of Faith that expresses our understanding of the Bible’s vision for the church to promote clarity and transparency at Silicon Valley Reformed Baptist Church."
  }]);
  const [conversationHistory_user, setConversationHistory_user] = useState([{
    role: "system", content: "You are a search engine expert specializing in creating queries to search a collection of books indexed using an inverted index. And you only reply with one search query."
  }]);

  async function onSubmit(event) {
    event.preventDefault();
    setIsLoading(true); // Set loading state to true
    try {
      setConversationStarted(true);

      // Update conversationHistory with the questionInput
      const newConversationHistory_user_1 = [...conversationHistory_user, { role: "user", content: questionInput }];

      // Start with CCEL query --> This will later be the section I want to replace with my DNN
      const response_query = await fetch("/api/ccel_query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: questionInput, conversationHistory_user }),
      });

      // Get the result from the CCEL query
      const adversary = await response_query.json();

      if (response_query.status !== 200) {
        throw adversary.error || new Error(`Request failed with status ${response_query.status}`);
      }

      // Update conversationHistory with the result from the CCEL query
      const newConversationHistory_user_2 = [...newConversationHistory_user_1, { role: "adversary", content: adversary.assistant.content },];

      // concat the result from the CCEL query with questionInput to get the new questionInput
      const new_questionInput = questionInput + "\nPlease consider the following books: \n" + adversary.assistant.content;

      // Main parrot
      const response_parrot = await fetch("/api/main_parrot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: questionInput, conversationHistory_parrot }),
      });

      const parrot = await response_parrot.json();

      if (response_parrot.status !== 200) {
        throw parrot.error || new Error(`Request failed with status ${response_parrot.status}`);
      }

      // Update conversationHistory with the result from the main parrot
      const newConversationHistory_parrot = [
        ...conversationHistory_parrot,
        { role: "user", content: questionInput },
        { role: "assistant", content: parrot.assistant.content },
      ];

      const newConversationHistory_user_3 = [...newConversationHistory_user_2, { role: "assistant", content: parrot.assistant.content }];
      
      // Update the state
      setQuestionInput("");
      setConversationHistory_parrot(newConversationHistory_parrot);
      console.log("newConversationHistory_parrot: ", newConversationHistory_parrot);
      
      setConversationHistory_user(newConversationHistory_user_3);
      console.log("newConversationHistory_user_3: ", newConversationHistory_user_3);
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
            conversationHistory_user.slice(1).map((message, index) => (
              <div
                key={index}
                className={`${styles.textBubble} ${message.role === "user"
                    ? styles.userBubble
                    : message.role === "assistant"
                      ? styles.calvinistParrotBubble
                      : styles.adversaryBubble
                  }`}
              >
                <p>
                  <strong>
                    {message.role === "user"
                      ? "Your question"
                      : message.role === "assistant"
                        ? "Calvinist Parrot"
                        : "Adversarial question"}
                    :</strong>{" "}
                  {message.content}
                </p>
              </div>
            ))}
        </div>


        <div className={styles.formContainer}>
          {isLoading && <span>Loading...</span>}
          <form onSubmit={onSubmit}>
            <input
              type="text"
              name="question"
              placeholder="ask a question"
              value={questionInput}
              onChange={(e) => setQuestionInput(e.target.value)}
            />
            <input type="submit" value="Ask" />
          </form>
        </div>
      </main>


    </div>
  );
}
