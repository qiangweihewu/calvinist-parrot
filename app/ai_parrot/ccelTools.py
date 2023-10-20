from langchain.tools import Tool
import requests, string

def formater(output):
    sources = {}
    alphabet = string.ascii_lowercase
    a = 0

    for source in output['source_nodes']:
        if source['node']['metadata']['title'] not in sources.keys():
            sources[source['node']['metadata']['title']] = {'authors': source['node']['metadata']['authors'], 'score': [f"{alphabet[a]}. {round(source['score'], 3)}"]}
        else:
            sources[source['node']['metadata']['title']]['score'].append(f"{alphabet[a]}. {round(source['score'], 3)}")
        a += 1

    source_text = "Sources:\n"
    n = 1

    for source in sources.keys():
        source_text += f"{n}. {source} by {sources[source]['authors']} - Confidence: {', '.join(sources[source]['score'])}\n"
        n += 1

    return source_text

def biblical_texts_and_commentaries(question):
    response = requests.post('https://biblical-texts-and-commentaries-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def christian_biography(question):
    response = requests.post('https://christian-biography-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def christian_devotional(question):
    response = requests.post('https://christian-devotional-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def christian_fiction(question):
    response = requests.post('https://christian-fiction-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def christian_life_and_worship(question):
    response = requests.post('https://christian-life-and-worship-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    print(output)
    return output['response'] + '\n\n' + formater(output)

def christian_living(question):
    response = requests.post('https://christian-living-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def christian_poetry(question):
    response = requests.post('https://christian-poetry-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def early_christian_fathers(question):
    response = requests.post('https://early-christian-fathers-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def early_christian_literature(question):
    response = requests.post('https://early-christian-literature-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def historical_and_biographical_texts(question):
    response = requests.post('https://historical-and-biographical-texts-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def miscellaneous_texts(question):
    response = requests.post('https://miscellaneous-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def reformed_commentaries(question):
    response = requests.post('https://reformed-commentaries-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def reformed_theology(question):
    response = requests.post('https://reformed-theology-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    print(output)
    return output['response'] + '\n\n' + formater(output)

def sermons(question):
    response = requests.post('https://sermons-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def systematic_theology(question):
    response = requests.post('https://systematic-theology-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def theology(question):
    response = requests.post('https://theology-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)

def theology_and_beliefs(question):
    response = requests.post('https://theology-and-beliefs-west2-e4y6sp3yrq-wl.a.run.app/query', json={'question': question})
    output = response.json()
    return output['response'] + '\n\n' + formater(output)


toolkit = [
    # Tool(
    #     name="Biblical Texts and Commentaries", 
    #     func=biblical_texts_and_commentaries, 
    #     description="Books focusing on the interpretation, analysis, and study of biblical texts. - Includes books like The Expositor's Bible: Ezra, Nehemiah, and Esther, The Expositor's Bible: The Song of Solomon and the Lamentations of Jeremiah, The Expositor's Bible: The Epistles of St. John and authors like Calvin, John (1509-1564), Robertson, A. T. (1863-1934), Maclaren, Alexander (1826-1910)."
    # ),
    # Tool(
    #     name="Christian Biography", 
    #     func=christian_biography, 
    #     description="Biographical accounts of notable Christian figures. - Includes books like Autobiography of George Fox, Entire Sanctification, Historia Calamitatum: The Story of My Misfortunes and authors like Voragine, Jacobus de (1230-1298), Fox, George (1624-1691), Clarke, Adam."
    # ),
    # Tool(
    #     name="Christian Devotional", 
    #     func=christian_devotional, 
    #     description="Books meant for daily Christian reflection, prayer, and meditation. - Includes books like A Book of Strife in the Form of the Diary of an Old Soul, Christ Altogether Lovely, Daily Meditations and Prayers and authors like MacDonald, George (1824-1905), Flavel, John (1630-1691), Bradford, John (1510-1555)."
    # ),
    # Tool(
    #     name="Christian Fiction", 
    #     func=christian_fiction, 
    #     description="Fictional works that emphasize Christian themes and values. - Includes books like The Pilgrim's Progress, The Innocence of Father Brown, Magic: A Fantastic Comedy and authors like MacDonald, George (1824-1905), Tolstoy, Leo Nikolayevich (1828-1910), Chesterton, Gilbert K (1874-1936)."
    # ),
    # Tool(
    #     name="Christian Life and Worship", 
    #     func=christian_life_and_worship, 
    #     description="Books on Christian practices, worship, and daily living. - Includes books like What I Saw in America, A COLLECTION OF LETTERS, A Confession and authors like Spurgeon, Charles Haddon (1834-1892), South, Robert, (1634-1716), Law, William (1686-1761)."
    # ),
    # Tool(
    #     name="Christian Living", 
    #     func=christian_living, 
    #     description="Guides and reflections on leading a Christian life. - Includes books like A Discourse concerning Evangelical Love, Church Peace, and Unity, A Persuasive to a Holy Life: from the Happiness Which Attends It Both in This World, and in the World to Come., A Selection from his Letters and authors like Owen, John (1616-1683), Murray, Andrew, Watson, Thomas."
    # ),
    # Tool(
    #     name="Christian Poetry", 
    #     func=christian_poetry, 
    #     description="Poetic works with Christian themes and expressions. - Includes books like Hymns from the Land of Luther, Hymns of Ter Steegen and Others (Second Series), Hymns of Ter Steegen, Suso, and Others and authors like Bevan, Frances, Brownlie, John, Walker, William (1809-1875)."
    # ),
    # Tool(
    #     name="Early Christian Fathers", 
    #     func=early_christian_fathers, 
    #     description="Writings from early Christian leaders and theologians. - Includes books like ECF: Aphrahat: Demonstrations, ECF: Eunomius: The First Apology, ECF: Hegesippus and authors like Pearse, Roger, Roger Pearse."
    # ),
    Tool(
        name="Early Christian Literature", 
        func=early_christian_literature, 
        description="Early texts, letters, and documents from the initial centuries of Christianity. - Includes books like ANF02. Fathers of the Second Century: Hermas, Tatian, Athenagoras, Theophilus, and Clement of Alexandria (Entire), ANF04. Fathers of the Third Century: Tertullian, Part Fourth; Minucius Felix; Commodian; Origen, Parts First and Second, ANF06. Fathers of the Third Century: Gregory Thaumaturgus, Dionysius the Great, Julius Africanus, Anatolius, and Minor Writers, Methodius, Arnobius and authors like Schaff, Philip (1819-1893) (Editor), Lightfoot, Joseph Barber (1828-1889), Pearse, Roger."
    ),
    # Tool(
    #     name="Historical and Biographical Texts", 
    #     func=historical_and_biographical_texts, 
    #     description="Accounts of Christian history and biographies of significant figures. - Includes books like Biography of John Owen, ECF: Possidius: Life of St. Augustine, Funeral Sermon on Dr John Owen and authors like Schaff, Philip (1819-1893), Harnack, Adolf (1851-1930), Bangs, Nathan, D.D.."
    # ),
    # Tool(
    #     name="Miscellaneous Texts", 
    #     func=miscellaneous_texts, 
    #     description="A diverse collection of Christian texts that don't fit neatly into other categories. - Includes books like Swiss Family Robinson, Easton's Bible Dictionary, Hitchcock's Bible Names Dictionary and authors like Pearse, Roger, Chesterton, Gilbert K. (1874-1936), Anonymous."
    # ),
    Tool(
        name="Reformed Commentaries", 
        func=reformed_commentaries, 
        description="Reformed books focusing on the interpretation, analysis, and study of biblical texts. - Includes books like Harmony of the Law - Volume 3, Preface to the Letter of St. Paul to the Romans, Why Four Gospels? and authors like Pink, Arthur W., Calvin, Jean, Calvin, John (1509 - 1564)."
    ),
    # Tool(
    #     name="Sermons", 
    #     func=sermons, 
    #     description="Collections of sermons within the CCEL - Includes books like Spurgeon's Sermons Volume 01: 1855, Spurgeon's Sermons Volume 59: 1913, Spurgeon's Sermons Volume 23: 1877 and authors like Donne, John (1572-1631), Latimer, Hugh (1485-1555), Bradford, John (1510-1555)."
    # ),
    Tool(
        name="Systematic Theology", 
        func=systematic_theology, 
        description="Comprehensive exploration of Christian doctrines and theology. - Includes books like A Body of Practical Divinity, Doctrinal Theology, History of Dogma - Volume IV and authors like Hodge, Charles (1797-1878), Hopkins, Samuel (1721-1803), Gill, John (1697-1771)."
    ),
    # Tool(
    #     name="Theology", 
    #     func=theology, 
    #     description="In-depth studies and discussions on various theological topics. - Includes books like A Brief Declaration and Vindication of The Doctrine of the Trinity, A Discourse on the Cleansing Virtue of Christ's Blood, A Display of Arminianism and authors like Owen, John (1616-1683), Schaff, Philip (1819-1893) (Editor), Cyril of Alexandria."
    # ),
    # Tool(
    #     name="Theology and Beliefs", 
    #     func=theology_and_beliefs, 
    #     description="Exploration of Christian beliefs, doctrines, and theological perspectives. - Includes books like The Evidences of Christianity Briefly Stated and the New Testament Proved to Be Genuine. In Three Judicious and Excellent Sermons., The Catholic Encyclopedia, Volume 1: Aachen-Assize, The Catholic Encyclopedia, Volume 10: Mass Music-Newman and authors like Herbermann, Charles George (1840-1916), Owen, John (1616-1683), Schaff, Philip (1819-1893) (Editor)."
    # )
]