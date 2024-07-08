
# Home page
HOME_TITLE = "Welcome to the Calvinist Parrot!"

HOME_INTRO = """\
Welcome! I'm here to guide you through the Bible from a Reformed perspective. Feel free to ask me anything about Scripture, and I'll provide insights based on my knowledge and understanding as a Reformed Baptist.

As an AI-driven application, I provide with multiple tools that gather information from sources like the [Christian Classics Ethereal Library](https://ccel.org) and [Bible Hub](https://biblehub.com/commentaries) to enhance your time in the Bible.

While I can't use the ESV due to restrictions, we rely on the Berean Standard Bible ([BSB](https://berean.bible/)) for our primary translation. Learn more about the BSB [here](https://copy.church/initiatives/bibles/) and join us in discovering the richness of its text.\
"""

HOME_MENU_INTRO = """\
Explore the tools available on the left menu:

- **Calvinist Parrot**: Engage in discussions and questions from a Reformed perspective on the Bible. Parrot, Calvin, and a CCEL Librarian are here to help you learn and grow in your understanding of Scripture.
- **CCEL**: Dive into the treasures of the [Christian Classics Ethereal Library](https://ccel.org) for timeless Christian writings.
- **Study Helper**: Access commentaries from [Bible Hub](https://biblehub.com/commentaries) to enrich your study of Scripture.
- **Devotionals**: Start or end your day with AI-generated morning and evening reflections for comfort and inspiration.
- **Sermon Review**: Evaluate your sermons using Bryan Chappell's Christ-Centered Preaching framework.\
"""

HOME_FOOTER = """\
- Feb 2024 update: Due to lack of funding, I'm depricating the "Main Chat" since the cost to maintain the CCEL index is too high. I'm sorry for the inconvenience. I'll keep the "Study Helper" and "Devotionals" tools available. I'm also working on a new tool to help you study the Bible. Stay tuned!
- Mar 2024 update: New sermon review tool is up! You can now review sermons using Bryan Chappell's evaluation framework from his book, Christ-Centered Preaching.
- June 2024 update: The CCEL tool is back!

Fair warning: Session management is a bit wonky. I'm working on it. iOS doesn't play very well with sessions. I'm sorry for the inconvenience.

I'm still learning, so please be patient with me! I'm always looking to improve, so if you have any feedback, <a href='mailto:jesus@jgmancilla.com'>please let me know</a>

I'm also open source, so if you're interested in contributing to my development, check out my [GitHub](https://github.com/Jegama/calvinist-parrot)\
"""

pages = [
    "Calvinist Parrot",
    "Study Helper",
    "Devotionals",
    "Sermon Review",
    "Bible Studies",
    "Log in",
    "Register",
    "Log out"
]

# Side menu
CLEAR_CHAT = "New Conversation"
LOGGED_AS = "Logged in as"
CHAT_HIST = "Chat History"
NOT_LOGGED = "Please log in to see your chat history"
NO_HIST = "No conversations yet. I'm looking forward to chatting with you!"

# Chat related
CONSULTED_SOURCES = "📚 **Counsulted Sources**"
CHAT_FIRST_MESSAGE = "What theological questions do you have?"
CHAT_PLACESHOLDER = "What is predestination?"
CHAT_NOT_LOGGED = "Please use the sidebar to log in or register."

# Errors
ERROR_CREATING_CONVERSATION = "Error updating or creating conversation"
ERROR_GETTING_HISTORY = "Error getting conversation history"
ERROR_CREATE_USER = "Failed to create user"

# CCEL
CCEL_FIRST_MESSAGE = "What do you want to learn?"

# Study Helper
SH_EXPANDER = "📚 **Additional information**"
SH_EXPANDER_SOURCE = "Source"
SH_FIRST = "What passage do you want to study?"
SH_PLACEHOLDER = "Can you help me understand this passage?"
SH_SPINNER = "Fetching commentaries..."
SH_CHECK_NONE = "Sorry, I couldn't find any references in your input. Please try again."
SH_CHECK_INDEXING = "Indexing commentaries..."
SH_CHECK_SUCCESS = "Commentaries indexed! What question do you have?"
SH_SPINNER_QUERY = "Thinking..."
SH_NO_QUERY_ENGINE = "❌ - We don't have a Query Engine..."
SH_YES_QUERY_ENGINE = "✅ - We have a Query Engine Active!"

# Devotionals
DEVOTIONALS_SPINNER = "Generating..."
DEVOTIONALS_FOOTER = "This devotional was generated by AI. If you have any questions or comments, please email [Jesús Mancilla](mailto:jesus@jgmancilla.com)"
DEVOTIONALS_EXPANDER = "📰 **Additional information**"
DEVOTIONALS_EXPANDER_TITLE = "News articles used to generate this devotional:"

# Sermon Review
SR_SIDE_NO_REVIEWS = "You haven't reviewed any sermons yet."
SR_SIDE_NEW_REVIEW = "New Review"
SR_DOWNLOAD_REVIEW = "Download Review"
SR_SPINNER_1 = "Generating first section... This takes at least 30 seconds."
SR_1_SUCCESS = "First section generated successfully."
SR_1_FAIL = "Failed to generate first section."
SR_SPINNER_2 = "Generating second section... This takes at least 30 seconds."
SR_2_SUCCESS = "Second section generated successfully."
SR_2_FAIL = "Failed to generate second section."
SR_NEW_REVIEW_HEADER = "What sermon would you like to review today?"
SR_NEW_REVIEW_INTRO = "The Calvinist Parrot uses Bryan Chappell's evaluation framework from his book, Christ-Centered Preaching, to evaluate sermons."
SR_SERMON_TITLE = "Enter the sermon title"
SR_PREACHER = "Enter the preacher's name"
SR_TRANSCRIPT = "Enter the sermon transcript"
SR_GENERATE_BUTTON = "Generate Review"
SR_NOT_ALL_FIELDS = "Please fill in all the fields."
SR_TRANSCRIPT_TOO_SHORT = "The transcript is too short. Are you sure this is the full sermon?"

# Log in
LOGIN_WELCOME = "To take full advantage of the Calvinist Parrot, please log in. If you don't have an account, you can register for free."
LOGIN_USERNAME = "Username"
LOGIN_PASSWORD = "Password"
LOGIN_BUTTON = "Log in"

# Register
REGISTER_WELCOME = "Register for free to access all the features of the Calvinist Parrot."
REGISTER_USERNAME_PLACEHOLDER = "This will be your login name"
REGISTER_NAME = "Name"
REGISTER_NAME_HELP = "The parrot will use this name to refer to you"
REGISTER_NAME_PLACEHOLDER = "John Doe"
REGISTER_PASSWORD_HELP = "Please use a strong password"
REGISTER_LANGUAGE = "Preferred language"
REGISTER_BUTTON = "Register"
languages = ["English", "Spanish"]
