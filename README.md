# The usage of love-related emoji in French and German on Twitter

## Introduction
Modern communication gets more and more enriched by the usage of emoji. These symbols provide additional cues about the intention and state of the mood of the participants in a purely text-based conversion. With the increasing amount of digital messages, this former Japanese trend spreads around the world. First linguistic start research regarding their usage and the information which may be encoded in it. 

In the paper “Learning from the Ubiquitous Language: an Empirical Analysis of Emoji Usage of Smartphone Users”, Lu et. al. analyze the usage of emoji on a large scale keyboard application for the mobile operating system Android. In their analysis of the regional difference between the 3.88 million users, they report especially for the French users of the keyboard two significant differences to other users: On the one hand, French users are supposed to use more emoji. On the other, they are assumed to employ a different subset of them more commonly; especially the usage of heart- and love-related symbols is reported to be more prevalent.

In this project for the course "Statistics for Linguistics with R" taught by Dr. Peter Uhrig at the University of Osnabrück, we try to build upon this finding. Our aim is not to replicate the results exactly but to test the hypothesis that the amount of love-related emoji in French tweets is significantly higher in comparison to German Tweets. It is important to stress out that the results are not covered nor directly comparable with the finding of the paper mentioned above. First of all, we solely focus on public Twitter data rather on data recorded both from the public as private communication. Secondly, we will consider the languages of the Tweets rather than the nationality of its author. Given the exclusion of intimate communication and the widespread use of French around the world, our results may therefore quite different in comparison to the analysis by the Chinese researchers.

## Method
The test of our hypothesis will follow the established procedure of conducting an experiment and proving a hypothesis. It will be implemented in a combination of Python and R where former will be used to aggregate the data and analyze it later. **Please be aware that this document is valid RMarkdown and might be used to replicate the results on your computer, i.e. in RStudio.**

In the following, we will consider only the emoji embedded into the tweets encoded in the Unicode standard. Latter is an international charset allowing the usage of characters outside the ASCII set like “Umlaute”. Currently, it includes 3019 emoji while still increasing due to running standardizations. As “love-related emoji” we define a subset both based on the finding in the paper mentioned above and our observations in everyday communication. In particular, we included:

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

In order of following the well-established patterns of an unbiased statistical workflow, we defined the critical core components of our experiment before having any look at the available data. Therefore, we define both the hypotheses and the asymptotic significance (p-value) of the experiment. As commonly defined, the H0 hypothesis refers to the current state of knowledge while H1 might be the hypothesis of interest evaluated with statistical methods. With a commonly utilized asymmetric significance of 5%, we will choose H1 wrongly.

```{r}
# Define the hypotheses
h0 = "Love-related emoji appear less or equally often in French tweets as in German tweets."
h1 = "Love-related emoji appear significantly more often in French tweets as in German tweets."

# Define the asymptotic significance aka the possible error we will choose h1 wrongly over h0
p = 0.05
```

Given these hypotheses, we analyzed the statistical methods of choice for proving them. In a nutshell, we are actually interested in comparing the underlying distribution behind the emoji usage. Given a number of samples high enough, those may follow the general distribution of emoji in those languages. Written more formally, we are interested in the distributions of a depended interval-scaled variable *number of love-related emoji* given an independent and nominal variable *language*.  One of the most common and robust approaches for dealing with such a comparison of distributions is the well-known Kolmogorov-Smirnov test which will be applied after the data extraction.

### Data

As already described above, the data processing pipeline is split into two components. A flexible Python script is used to process the raw data from Twitter and export it into a tab-separated text file. Afterward, this file is imported into R where the data is filtered, formatted and finally tested regarding our hypotheses.

For extracting the data, please prepare your available Twitter data in a text file where each line represents a single tweet encoded as an individual *JSON* object and install the required dependencies with `pip install -r requirements.txt`.  A sequential call of `python extract_emojis.py --help` will give you an extensive overview of the parameters which might be used for customizing the extraction process. Due to privacy and copyright concerns we do not publish the original tweet data of our research but the anonymized output after the extraction process. You find them in the *emoji.tsv* file. After the extraction process, one may finally load and analyze the data in R.

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

After the load of the data and the removal of tweets containing no emoji, the fact may cache someone's eye that the two groups have significantly different sizes. Therefore, in order of excluding biases simply due to the amount of data available, the size of all datasets is adjusted by randomly sampling as many samples as in the smallest group.

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

Afterward, the data is ready to get analyzed. The number of love-related emoji get counted and exported into a new `data.frame` allowing straightforward access. Additionally, a small amount of noise is added to the numbers. Rather than integers, the data gets converted into a floating number. This allows, in the first step, a more clear plotting of the data. In the resulting strip chart, the rough distribution between both expressions of the independent variable could be observed.

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

# Extract a human-readable overview and add a small amount of noise to the samples
love_emoji_by_language = list(
  "French" = jitter(love_emoji[love_emoji$LANGUAGE == 'fr', 'NUM_EMOJI'], factor = 0.2),
  "German" = jitter(love_emoji[love_emoji$LANGUAGE == 'de', 'NUM_EMOJI'], factor = 0.2)
)

# Visualize the data
stripchart(love_emoji_by_language, xlab="Number of love-related emoji", ylab="Language")
```

## Results
Finally, the actual statistical test is applied to the preprocessed data. It is worth to mention that our raw data is, strictly speaking, not suitable for the Kolmogorov-Smirnov test. Even if being extremely robust against the violation of this assumption, it expects a continuous distribution. Therefore, the added noise in the last step does not only suite visualization purposes. Instead, it removed ties and simulates, therefore, such a type of distribution. While the rough shape of the data remains the same, the tiny numerical differences ensure the stability of the test. As we test especially that the distribution of the love-related emoji is significantly higher in French, a one-sided test is used.

```{r}
# Execute the two-sample and one-sided Kolmogorov-Smirnov test
test_result = ks.test(love_emoji_by_language[["French"]], love_emoji_by_language[["German"]], alternative="greater")

# Interpret the results
cat(
"According to a two-sample and one-sided Kolmogorov-Smirnov test,",
if(test_result[['p.value']] < p) "H0 can be rejected." else "H0 still holds.",
if(test_result[['p.value']] < p) h1 else h0,
"Calculated significance:", test_result[['p.value']]
)
```

On our dataset, we were unable to show a significantly higher number of love-related emoji in French tweets in comparison to German ones. Instead, the distributions might be seen as rather similar. Follow-up studies may focus on the reasons for these discrepancies in comparison to the results of Lu. As already presented in the introduction, multiple reasons for these variations seems imaginable. The difference may explainable by the observation that the usage of the tiny pictures is a matter of the country of origin rather than the used language. Bots or other noise may have tamped the data up to a specific point; the usage of bigger amount of data may help to reduce such a risk. Or we may have, as the possible most "pleasant" interpretation, demonstrated one of the fundamental rules for the responsible use of social media: If a message is private and intimate, it should not be publicly accessible. Especially not on Twitter.