# The usage of love-related emoji in French and German on Twitter

## Introduction
Modern communication gets more and more enriched by the usage of Emoji. These symbols provide additional cues about the intention and state of mood of the participants in a purely text based conversion. With the increasing amount of digital messages, these former Japanese symbols spread around the world. First research is starting regarding their usage and the information which may be encoded in their usage. 

In the paper “Learning from the Ubiquitous Language: an Empirical Analysis of Emoji Usage of Smartphone Users”, Lu et. al. analyze the usage of emoji on a large scale keyboard application for the mobile operation system Android. In their analysis of the regional difference between the 3.88 million users, they report especially for the French users of the keyboard two significant differences to other user: On the one hand, French users are supposed to use more emoji. On the other, they are supposed to use a different subset of emoji more commonly; especially the usage of heart- and love-related symbols is reported to be more common.

In this project for the course "Statistics for Linguistics with R" taught by Dr. Peter Uhrig at the University of Osnabrück, we try to build upon this finding. Our aim is not to replicate the results exactly but  to test the hypothesis that the amount of love-related emoji in French tweets is significantly higher in comparison to German Tweets. It is important to stress out that the results are not covered nor directly comparable with the finding of the paper mentioned above. First of all, we soly focus on public Twitter data rather on data recorded both from public as private communication. Secondly, we will consider the languages of the Tweets rather than the nationality of its author. Given the exclusion of intimate communication and the widespread use of French around the world, our results may therefore quite different in comparison to the analysis by the Chinese researchers.

## Method
The test of our hypothesis will follow the classical way of proving a hypothesis. The experiment will be implemented in a combination of Python and R where former will be used to aggregate the data and latter to analyze it. **Please be aware that this document is valid RMarkdown and might be used to replicate the results on your computer.**

As love-relard emoji we define a subset defined by the Unicode standart. In special, we included:

```{r}
# Define the subset of emoji of interest
emoji = factor(c(
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
))
```

In order of following the well-established patterns of unbiased statistical workflow, we defined the core components of our experiment before having any look at the available data. Therefore, we define both the hypotheses and the asymptotic significance (p-value) of the experiment:

```{r}
# Define the hypotheses
h0 = "Love-related emoji appear less or equally often in French tweets as in German tweets."
h1 = "Love-related emoji appear significantly more often in French tweets as in German tweets."

# Define the asymptotic significance aka the possible error we will choose h1 wrongly over h0
p = 0.05
```

Starting from this definitions, we defined the exact type of our experiment. As already encoded in the hypotheses, we are actually comparing distributions of a depended interval-scaled variable *number of love-related emoji* given a independent and nominal variable *language*.  One of the most common and robust approaches for dealing with such a comparison of distributions is the Kolmogorov-Smirnov test. In order of getting statistically relevant results, one had to parse the Twitter data.

### Data

As already described above, the data processing pipeline is split into two components. A flexible Python script is used to process the raw data from Twitter and export it into a tab-separated text file. Afterwards, this file is imported into R where the data is filtered, formatted and finally tested regarding our hypotheses.

For extracting the data, please prepare a text file where each line represents a single tweet encoded as an individual *JSON* object. Install dependencies with `pip install -r requirements.txt`.  A sequential call of `python extract_emojis.py --help` will give you an extensive overview over the parameters which might be used for the extraction process. Due to privacy and copyright concerns we do not publish the original tweet data but the anonymized output after the extraction process. You find them in the *emoji.tsv* file. After the extraction process, we may finally load the data into R.

```{r}
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
      FUN=function(vector) all(vector)
  )
  num_tweets_with_emoji = sum(tweets_with_emoji)
  
  # Print the result
  cat("Language '", language, "': ", num_tweets_with_emoji, "/", num_tweets, " tweets written with emoji.\n", sep='')
  
  # Filter out all tweets without emoji
  tweets[[language]] = tweets[[language]][tweets_with_emoji]
}
```

After the load of the data and the removal of tweets containing no emoji, the fact may cache someones eye that the two groups have significantly different sizes. Therefore, in order of excluding biases simply due to the amount of data available, the size of all datasets is adjusted by randomly sampling as much samples as in the smallest group. 

```{r}
# Find the language with the fewest tweets and get their number
min_num_tweets = min(sapply(tweets, FUN=function(x) length(x)))

# Iterate through all languages ...
for (language in names(tweets)) {
  num_tweets = length(tweets[[language]])
  
  # ... and sub-sample those with more tweets.
  if(num_tweets > min_num_tweets) {
    tweets[[language]] = sample(tweets[[language]], min_num_tweets)
  }
}

cat("The amount of tweets for each language were downsampled to", min_num_tweets, "tweets.")
```

Afterwards, the data is ready to get analyzed. The number of love-related emoji get counted and exported into a new data.frame allowing a straightforward access. As the final sanity check, the data is plotted with a specific jitter. In the resulting stripchart, the rough distribution between both expressions of the independent variable could be observed.

```{r}
#' Count the number of emoji from a specific set
count_emoji <- function(tweets, emoji_set, num_tweets_per_language) {
  love_emoji = c()
  languages = c()
  
  # Iterate through languages ...
  for (language in names(tweets)) {
    # ... and count the emoji in the set.
    num_love_emoji = unlist(
      lapply(tweets[[language]], function(x) sum(x$EMOJI %in% emoji_set)), 
      use.names=FALSE
    )
    
    love_emoji = append(love_emoji, num_love_emoji)
    languages = append(languages, rep(language, num_tweets_per_language))
  }
  
  # Create a data.frame from both vectors
  return(data.frame(
    NUM_EMOJI = love_emoji,
    LANGUAGE = languages,
    stringsAsFactors = TRUE
  ))
}

# Extract the emoji
love_emoji = count_emoji(tweets, emoji, min_num_tweets)

# Extract a human-readable overview
love_emoji_by_language = list(
  "French" = love_emoji[love_emoji$LANGUAGE == 'fr', 'NUM_EMOJI'],
  "German" = love_emoji[love_emoji$LANGUAGE == 'de', 'NUM_EMOJI']
)

# Visualize the data
stripchart(love_emoji_by_language, method="jitter",xlab="Number of love-related emoji", ylab="Language")
```

## Results
Finally, the actual test may be applied on the preprocessed data. As the Kolmogorov-Smirnov test does not work well with ties, the jitter already shown above is applied. While the rough shape of the distribution remains the same, the tiny numerical differences ensure the stability of the test. 

```{r}
# Execute the two-sample and one-sided Kolmogorov-Smirnov test
test_result = ks.test(love_emoji_by_language[["French"]], love_emoji_by_language[["German"]], alternative="greater")

# Interpret the results
cat(
"According to a two-sample and one-sided Kolmogorov-Smirnov test,",
if(test_result[['p.value']] < p) "H0 can be rejected." else "H0 still holds.",
if(test_result[['p.value']] < p) h1 else h0
)
```

On our dataset, we were unable to show a significant higher number of love-related emoji in French tweets in comparison to German ones. Instead, the distributions appear rather similar. Follow-up studies may focus on the reasons for this differences in comparison to the results of Lu et. Al. As already presented in the introduction, multiple reasons seems imaginable. The difference may explainable by the observation that the usage of the tiny pictures is a matter of the country of origin rather than the used language. Bots or other noise may have tamped the data up to a specific point; the usage of bigger amount of data may help to reduce such a risk. But most possible, we may have demonstrated one of the fundamental rules for a responsible usage of social media: If a message is private and intimate, it should not be public accessible. Especially not on Twitter.