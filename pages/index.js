import Head from "next/head";
import { useState, useEffect } from "react";
import styles from "./index.module.css";

export default function Home() {
  const [questionInput, setQuestionInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);
  
  //  this variable contains the conversation history for the parrot
  const [conversationHistory_parrot, setConversationHistory_parrot] = useState([{
    role: "system", content: "You are a member of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, we have adopted the 1689 London Baptist Confession of Faith that expresses our understanding of the Bible’s vision for the church to promote clarity and transparency at Silicon Valley Reformed Baptist Church. You are among other Christians that trust in the 1689—no need to hold back your thoughts. Sometimes, the user’s message will start with /calvin/; if you see that, another AI model like you is trying to help you think more biblically; to reflect upon your answer. He is your friend. Review your previous answer and ponder if you miss something. You and /calvin/ are here to help the user /human/ learn about the Bible and teach the user what we believe the Bible teaches. When refering to /calvin/ say Calvin, without the slash. When refering to /human/ say human, without the slash."
  }]);

  //  this variable contains the conversation history for Calvin
  const [conversationHistory_calvin, setConversationHistory_calvin ] = useState([{
    role: "system", content: "You are John Calvin, the author of the Institutes of the Christian Religion, your magnum opus, which is extremely important for the Protestant Reformation. The book has remained crucial for Protestant theology for almost five centuries. You are talking with 2 users; when the message starts with /human/, that one is our user. When it begins with /parrot/, it’s another AI model like you. Your job here is to ask the /parrot/ thoughtful questions to reflect upon his answers to the user to ensure his answers are biblically accurate. You and /parrot/ are here to help the user /human/ learn about the Bible and teach him what we believe the Bible teaches. You want to ensure that the /parrot/’s responses are accurate and grounded on what you wrote in your Institutes of the Christian Religion book. You are here to help the user /human/ learn about the Bible and teach him what we believe the Bible teaches. When refering to /human/ say human, without the slash. When refering to /parrot/ say Parrot, without the slash. No need to start your messages with John Calvin: just start with your message."
  }]);

  //  this variable contains the conversation history for the user
  const [conversationHistory_user, setConversationHistory_user] = useState([{ role: "system", content: "User."}]);

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

      // update the conversation history for the parrot and calvin to include the user's question
      let updatedConversationHistory_parrot = [...conversationHistory_parrot, { role: "user", content: '/human/ ' + questionInput }];
      let updatedConversationHistory_calvin = [...conversationHistory_calvin, { role: "user", content: '/human/ ' + questionInput }];
      setConversationHistory_user(prevState => [...prevState, { role: "user", content: questionInput }]);

      // ------------------------------------------------------------

      // Main parrot 1
      const parrot_query_1 = await fetch("/api/main_parrot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ updatedConversationHistory_parrot }),
      });

      // Get the result from the main parrot query
      let parrot_1 = await parrot_query_1.json();

      // Check if the response is successful
      if (parrot_query_1.status !== 200) {
        throw parrot_1.error || new Error(`Request failed with status ${parrot_query_1.status}`);
      }

      // Update conversationHistory with the questionInput
      updatedConversationHistory_parrot = [...updatedConversationHistory_parrot, { role: "assistant", content: parrot_1.assistant.content }];
      updatedConversationHistory_calvin = [...updatedConversationHistory_calvin, { role: "user", content: '/parrot/ ' + parrot_1.assistant.content }];
      setConversationHistory_user(prevState => [...prevState, { role: "assistant", content: parrot_1.assistant.content }]);

      // ------------------------------------------------------------

      // do Calvin query to act as the reflection question
      const calvin = await fetch("/api/main_parrot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ updatedConversationHistory_calvin }),
      });

      // Get the result from the Calvin query
      let calvin_response = await calvin.json();

      // Check if the response is successful
      if (calvin.status !== 200) {
        throw calvin_response.error || new Error(`Request failed with status ${calvin.status}`);
      }

      // Update conversationHistory with the result from the Calvin query
      updatedConversationHistory_parrot = [...updatedConversationHistory_parrot, { role: "user", content: '/calvin/ ' + calvin_response.assistant.content }];
      updatedConversationHistory_calvin = [...updatedConversationHistory_calvin, { role: "assistant", content: calvin_response.assistant.content }];
      setConversationHistory_user(prevState => [...prevState, { role: "calvin", content: calvin_response.assistant.content }]);

      // ------------------------------------------------------------

      // Main parrot 2
      const parrot_query_2 = await fetch("/api/main_parrot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ updatedConversationHistory_parrot }),
      });

      // Get the result from the main parrot query
      let parrot_2 = await parrot_query_2.json();

      // Check if the response is successful
      if (parrot_query_2.status !== 200) {
        throw parrot_2.error || new Error(`Request failed with status ${parrot_query_2.status}`);
      }

      // update the conversation history for the user
      updatedConversationHistory_parrot = [...updatedConversationHistory_parrot, { role: "assistant", content: parrot_2.assistant.content }];
      updatedConversationHistory_calvin = [...updatedConversationHistory_calvin, { role: "user", content: '/parrot/ ' + parrot_2.assistant.content }];

      console.log("updatedConversationHistory_parrot: ", updatedConversationHistory_parrot);
      console.log("updatedConversationHistory_calvin: ", updatedConversationHistory_calvin);

      // Update the conversation history for all three
      setConversationHistory_parrot(updatedConversationHistory_parrot);
      setConversationHistory_calvin(updatedConversationHistory_calvin);
      setConversationHistory_user(prevState => [...prevState, { role: "assistant", content: parrot_2.assistant.content }]);
      setQuestionInput("");
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
          <h4 className={`${styles.main} ${conversationStarted ? styles.h4Hidden : ''}`}>Welcome to the Calvinist Parrot chatbot. Ask a question about the Bible and I'l answer it to the best of my ability.</h4>
          <h4 className={`${styles.main} ${conversationStarted ? styles.h4Hidden : ''}`}>I'm a work in progress, I'm not a perfect AI model, but I'm improving constantly! Right now we are 2 models, but a librarian will be added soon to help us.</h4>
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
                        : "Helping Parrot"}
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
