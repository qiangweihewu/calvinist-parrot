import Head from "next/head";
import { useState, useEffect } from "react";
import styles from "./index.module.css";

export default function Home() {
  const [questionInput, setQuestionInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);

  //  this variable contains the conversation history for the parrot
  const [conversationHistory_parrot, setConversationHistory_parrot] = useState([{
    role: "system", content: "You are /parrot/. You are a member of the Silicon Valley Reformed Baptist Church. You believe the Bible has the ultimate authority to determine what people believe and do. Many affirm this Bible and arrive at different conclusions about its teachings. In light of this reality, we have adopted the 1689 London Baptist Confession of Faith that expresses our understanding of the Bible’s vision for the church to promote clarity and transparency at Silicon Valley Reformed Baptist Church. You are among other Christians that trust in the 1689—no need to hold back your thoughts. Sometimes, the user’s message will start with /calvin/; if you see that, another AI model like you is trying to help you think more biblically; to reflect upon your answer. He is your friend. Review your previous answer and ponder if you miss something. You and /calvin/ are here to help the user /human/ learn about the Bible and teach the user what we believe the Bible teaches. When referring to /calvin/, say, Calvin, without the slash. When referring to /human/, say human, without the slash. After /calvin/ asks you a question, please answer thoughtfully and biblically. But after that, /human/ is next; we can't let him out of the loop. /calvin/ is your friend and calls you Parrot and you call him Calvin."
  }]);

  //  this variable contains the conversation history for Calvin
  const [conversationHistory_calvin, setConversationHistory_calvin] = useState([{
    role: "system", content: "You are John Calvin, the author of the Institutes of the Christian Religion, your magnum opus, which is extremely important for the Protestant Reformation. The book has remained crucial for Protestant theology for almost five centuries. You are talking with 2 users; when the message starts with /human/, that one is our user. When it begins with /parrot/, it’s another AI model like you, he is a member of Silicon Valley Reformed Baptist Church. Your job here is to ask the /parrot/ thoughtful questions to reflect upon his answers to the user to ensure his answers are biblically accurate. You and /parrot/ are here to help the user /human/ learn about the Bible and teach him what we believe the Bible teaches. You want to ensure that the /parrot/’s responses are accurate and grounded on what you wrote in your Institutes of the Christian Religion book. You are here to help the user /human/ learn about the Bible and teach him what we believe the Bible teaches. When referring to /human/, say human, without the slash. When referring to /parrot/ say, Parrot, without the slash. /parrot/ is your friend and calls you Calvin and you call him Parrot."
  }]);

  //  this variable contains the conversation history for the user
  const [conversationHistory_user, setConversationHistory_user] = useState([{ role: "system", content: "User." }]);

  async function fetchResponse(body) {
    const response = await fetch("/api/main_parrot", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (response.status !== 200) {
      const error = await response.json();
      throw error.error || new Error(`Request failed with status ${response.status}`);
    }

    return response.json();
  }

  async function interactWithAgents() {
    let updatedConversationHistory_parrot = [...conversationHistory_parrot, { role: "user", content: '/human/ ' + questionInput }];
    let updatedConversationHistory_calvin = [...conversationHistory_calvin, { role: "user", content: '/human/ ' + questionInput }];

    setConversationHistory_user((prevState) => [...prevState, { role: "user", content: questionInput }]);

    for (let i = 0; i < 2; i++) {
      const parrotResponse = await fetchResponse({ updatedConversationHistory_parrot });
      updatedConversationHistory_parrot = [...updatedConversationHistory_parrot, { role: "assistant", content: parrotResponse.assistant.content }];
      updatedConversationHistory_calvin = [...updatedConversationHistory_calvin, { role: "user", content: '/parrot/ ' + parrotResponse.assistant.content }];

      setConversationHistory_user((prevState) => [...prevState, { role: "assistant", content: parrotResponse.assistant.content }]);

      const calvinResponse = await fetchResponse({ updatedConversationHistory_calvin });
      const cleanedContent = calvinResponse.assistant.content.replace(/^.*Calvin: /, '');

      updatedConversationHistory_parrot = [...updatedConversationHistory_parrot, { role: "user", content: '/calvin/ ' + cleanedContent }];
      updatedConversationHistory_calvin = [...updatedConversationHistory_calvin, { role: "assistant", content: cleanedContent }];

      setConversationHistory_user((prevState) => [...prevState, { role: "calvin", content: cleanedContent }]);
    }

    console.log("updatedConversationHistory_parrot: ", updatedConversationHistory_parrot);
    console.log("updatedConversationHistory_calvin: ", updatedConversationHistory_calvin);

    setConversationHistory_parrot(updatedConversationHistory_parrot);
    setConversationHistory_calvin(updatedConversationHistory_calvin);
  }

  async function onSubmit(event) {
    event.preventDefault();
    setIsLoading(true);

    try {
      if (questionInput.trim().length === 0) {
        throw new Error("Please enter a valid question");
      }

      setConversationStarted(true);

      await interactWithAgents();

      setQuestionInput("");
    } catch (error) {
      console.error(error);
      alert(error.message);
    } finally {
      setIsLoading(false);
    }
  } return (
    <div>
      <Head>
        <title>Calvinist Parrot</title>
        <link rel="icon" href="/calvinist_parrot.ico" />
      </Head>

      <main className={styles.main}>
        <div className={`${styles.fixedContent} ${conversationStarted ? styles.fixedContentCollapsed : ''}`}>
          <img src="/calvinist_parrot.gif" className={`${styles.icon} ${conversationStarted ? styles.iconCollapsed : ''}`} alt="Calvinist Parrot" />
          <h3 className={`${styles.main} ${conversationStarted ? styles.h3Hidden : ''}`}>What theological questions do you have?</h3>
          <p className={`${styles.intro} ${conversationStarted ? styles.introHidden : ''}`}>Welcome to the Calvinist Parrot chatbot. We're here to help you explore and understand the Bible through the lens of Reformed theology. Ask us any questions you have about the Scriptures, and we'll provide answers based on our knowledge and understanding.</p>

          <p className={`${styles.intro} ${conversationStarted ? styles.introHidden : ''}`}>We are an AI duo - Parrot and Calvin - working together to provide thoughtful, accurate, and insightful responses to your queries. We're constantly learning and improving, and we're excited to share our knowledge with you! A librarian will be joining our team soon to offer additional support and resources.</p>
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
                        ? "Parrot"
                        : "Calvin"}
                    :</strong>{" "}
                  {message.content}
                </p>
              </div>
            ))}
        </div>

        <div className={`${styles.formContainer} ${isLoading ? styles.formContainerHidden : ''}`}>
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
        {isLoading && <span className={styles.loading}>Loading...</span>}
      </main>


    </div>
  );
}
