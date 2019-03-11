## Introduction
Modern communication gets more and more enriched by the usage of Emoji. These symbols provide additional cues about the intention and state of mood of the paricipants in a purely text based conversion. With the increasing amount of digital messages, these former Japanese symbols spread arount the world. First research is starting regarding their usage and the information which may be encoded in their usage. 

In the paper “Learning from the Ubiquitous Language: an Empirical Analysis of Emoji Usage of Smartphone Users”, Lu et. al. analyze the usage of emojis on a large scale keyboard application for the mobile operation system Android. In their analysis of the regional difference between the 3.88 million users, they report especially for the French users of the keyboard two significant differences to other user: On the one hand, French users are supposed to use more emojis. On the other, they are supposed to use a different subset of emojis more commonly; especially the usage of heart- and love-related symbols is reported to be more common.

In this project for the course "Statistics for Linguistics with R" taught by Dr. Peter Uhrig at the University of Osnabrück, we try to build upon this finding. Our aim is not to replicate the results exactly but  to test the hypothesis that the amount of love-related emoji in French tweets is significantly higher in comparison to German Tweets. It is important to stress out that the results are not covered nor not directly comparable with the finding of the paper mentioned above. First of all, we soly focus on public Twitter data rather on data recorded both from public as private communication. Secondly, we will consider the languages of the Tweets rather than the nationality of its author. Given the exclusion of intime communication and the widespread use of French around the world, our results may therefore quite different in comparsion to the analysis by the Chinese researchers.

## Method
The test of our hypothesis will follow the classical way of proving a hypothesis. The experiment will be implemented in a combination of Python and R where former will be used to aggregate the data and latter to analyze it. Please be aware that this document is valid RMarkdown and might be used to replicate the results on your computer.

We use the popular platform Twitter as the source of our data. The 
As love-relard emoji we define a subset defined by the Unicode standart. In special, we included:

```{r}
# Define the subset of emoji of interest
emoji = c(
  "smiling face with hearts",
  "smiling face with heart-eyes",
  "face blowing a kiss",
  "kissing face",
  "kissing face with closed eyes",
  "kissing face with smiling eyes",
  "smiling cat with heart-eyes",
  "kissing cat",
  "kiss mark",
  "love letter",
  "heart with arrow",
  "heart with ribbon",
  "sparkling heart",
  "growing heart",
  "heating heart",
  "living hearts",
  "two two hearts",
  "heart decoration",
  "heart exclamation",
  "broken heart"
)

# Read the data from the generated tsv file and seperate the tweets into French and German.
tweets = read.table(file = 'emoji.tsv', sep = '\t', header = TRUE)
tweets = split(tweets, tweets$LANGUAGE)

# Iterate trough languages and extract tweets with emoji
for (language in names(tweets)) { 
  # Create subframes for each individual tweet by its ID
  tweets[[language]] = split(tweets[[language]], tweets[[language]]$TWEET)
  
  # Calculate number of available tweets and find those containing emoji
  num_tweets = length(tweets[[language]])
  tweets_with_emoji = sapply(
      lapply(tweets[[language]], FUN = function(x) as.character(x$EMOJI) != ""), 
      FUN=function(vector) isTRUE(vector)
  )
  num_tweets_with_emoji = sum(tweets_with_emoji)
  
  # Print the result
  cat("Language '", language, "': ", num_tweets_with_emoji, "/", num_tweets, " tweets written with emoji.\n", sep='')
  
  # Filter out all tweets without emoji
  tweets[[language]] = tweets[[language]][tweets_with_emoji]
}
```