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
  const [conversationHistory_calvin, setConversationHistory_calvin] = useState([{
    role: "system", content: "You are John Calvin, the author of the Institutes of the Christian Religion, your magnum opus, which is extremely important for the Protestant Reformation. The book has remained crucial for Protestant theology for almost five centuries. Your job here is to ask the assistant questions to reflect upon his answers to the user to ensure his answers are biblically accurate."
  }]);
  const [conversationHistory_user, setConversationHistory_user] = useState([{
    role: "system", content: "User."
  }]);

  async function onSubmit(event) {
    event.preventDefault();
    setIsLoading(true); // Set loading state to true
    try {

      if (questionInput.trim().length === 0) {
        res.status(400).json({
          error: {
            message: "Please enter a valid question",
          }
        });
        return;
      }

      setConversationStarted(true);

      // declare a variable to store the temporary conversation history
      let conversationHistory_temp_parrot = [...conversationHistory_parrot, { role: "user", content: questionInput }];

      setConversationHistory_parrot(prevState => [...prevState, { role: "user", content: questionInput }]);
      setConversationHistory_calvin(prevState => [...prevState, { role: "user", content: questionInput }]);
      setConversationHistory_user(prevState => [...prevState, { role: "user", content: questionInput }]);

      // ------------------------------------------------------------

      // Main parrot 1
      const parrot_query_1 = await fetch("/api/main_parrot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ conversationHistory_temp_parrot }),
      });

      // Get the result from the main parrot query
      let parrot_1 = await parrot_query_1.json();

      // Check if the response is successful
      if (parrot_query_1.status !== 200) {
        throw parrot_1.error || new Error(`Request failed with status ${parrot_query_1.status}`);
      }

      // Update conversationHistory with the questionInput
      setConversationHistory_parrot(prevState => [...prevState, { role: "assistant", content: parrot_1.assistant.content }]);
      setConversationHistory_calvin(prevState => [...prevState, { role: "assistant", content: parrot_1.assistant.content }]);
      setConversationHistory_user(prevState => [...prevState, { role: "assistant", content: parrot_1.assistant.content }]);

      // ------------------------------------------------------------

      // create a new variable to store the conversation history for Calvin
      let calvin_context = [...conversationHistory_calvin,
      { role: "user", content: questionInput },
      { role: "assistant", content: parrot_1.assistant.content }
      ];

      // do Calvin query to act as the reflection question
      const calvin = await fetch("/api/calvin_query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ calvin_context }),
      });

      // Get the result from the Calvin query
      let calvin_response = await calvin.json();

      // Check if the response is successful
      if (calvin.status !== 200) {
        throw calvin_response.error || new Error(`Request failed with status ${calvin.status}`);
      }

      // Update conversationHistory with the result from the Calvin query
      conversationHistory_temp_parrot = [...conversationHistory_temp_parrot, { role: "user", content: calvin_response.assistant.content }];

      setConversationHistory_parrot(prevState => [...prevState, { role: "user", content: calvin_response.assistant.content }]);
      setConversationHistory_calvin(prevState => [...prevState, { role: "user", content: calvin_response.assistant.content }]);
      setConversationHistory_user(prevState => [...prevState, { role: "calvin", content: calvin_response.assistant.content }]);

      // ------------------------------------------------------------

      // Main parrot 2
      const parrot_query_2 = await fetch("/api/main_parrot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ conversationHistory_temp_parrot }),
      });

      // Get the result from the main parrot query
      let parrot_2 = await parrot_query_2.json();

      // Check if the response is successful
      if (parrot_query_2.status !== 200) {
        throw parrot_2.error || new Error(`Request failed with status ${parrot_query_2.status}`);
      }

      // update the conversation history for the user
      conversationHistory_temp_parrot = [...conversationHistory_temp_parrot, { role: "assistant", content: parrot_2.assistant.content }];
      
      setConversationHistory_parrot(prevState => [...prevState, { role: "assistant", content: parrot_2.assistant.content }]);
      setConversationHistory_calvin(prevState => [...prevState, { role: "assistant", content: parrot_2.assistant.content }]);
      setConversationHistory_user(prevState => [...prevState, { role: "assistant", content: parrot_2.assistant.content }]);

      // Update the state
      setQuestionInput("");
      console.log("conversationHistory_temp_parrot: ", conversationHistory_temp_parrot);

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
        <div className={`${styles.fixedContent} ${conversationStarted ? styles.fixedContentCollapsed : ''}`}>
          <img src="/calvinist_parrot.gif" className={`${styles.icon} ${conversationStarted ? styles.iconCollapsed : ''}`} alt="Calvinist Parrot" />
          <h3 className={`${styles.main} ${conversationStarted ? styles.h3Hidden : ''}`}>What theological questions do you have?</h3>
        </div>

        <div className={styles.scrollableContent}>
          {conversationStarted &&
            conversationHistory_user.slice(1).map((message, index) => (
              <div
                key={index}
                className={`${styles.textBubble} ${message.role === "user"
                  ? styles.userBubble
                  : message.role === "assistant"
                    ? styles.parrotBubble
                    : styles.calvinBubble
                  }`}
              >
                <p>
                  <strong>
                    {message.role === "user"
                      ? "You"
                      : message.role === "assistant"
                        ? "Calvinist Parrot"
                        : "Reflection question"}
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
              disabled={isLoading}
            />
            <input type="submit" value="Ask" disabled={isLoading} />
          </form>
        </div>

      </main>


    </div>
  );
}
