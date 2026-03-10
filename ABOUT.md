# About

Project title: Dammit Macroeconomics Tracker

Team Name: Dammit SWE

## Project Description

Dammit Macroeconomics Tracker is a macro intelligence dashboard for asset managers. It aggregates financial news into one stream, then uses NLP and LLM classification to extract entities, detect sentiment, score event importance, and map events to persistent macro themes. Each theme has a live heat score and timeline so users can see how topics are heating up or cooling down across regions and asset classes. By replacing manual search and monitoring with automated clustering and risk interpretation, the platform reduces information overload and missed signals.

Due to limited time, only a simple data pipeline and some features could be implemented. More time is required to finetune NLP and LLM models and increase sources of ingestion. A deployed preview can be viewed at our [website](https://nfc-hackathon.vercel.app/).

### Features

News Feed

- Displays articles based on recency and importance scores

Trending themes

- Provides a heatmap of themes configured by the user

Chatbot

- RAG based chatbot that retrieves related articles from database
- Compresses, labels and stores past sessions which are used for reference in the future

Notifications

- Users can set thresholds for themes that create alerts when exceeded

Timeline

- Displays notable events related to a theme on a timeline
- Compacts events into single summaries for themes tracked over long periods of time
