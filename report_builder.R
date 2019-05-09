#Recieve filename
args = commandArgs(trailingOnly=TRUE)

#Ensure at least one argument
if (length(args)!=1) {
    stop(paste0("Directory name required.",length(args)),
         call.=FALSE)
}

set.seed(3223)

filename = args[1]
filename = gsub("/channels", "", filename)
class_name = strsplit(filename, "/")[[1]][2]
df = read.csv(paste0(filename,"/weekly_wordcount.csv"), header = T)

#Select most recent week
df = df[as.Date(df$date) == max(as.Date(df$date)),]
df$user <- as.character(df$user)

#Update grade book
grade_file <- paste0('resources/',class_name,"_grades.csv")
grades = read.csv(grade_file, header = T)
grades[,as.character(df$date[1])] <-rep(0,nrow(grades))
grades$user <- as.character(grades$user)

for (name in grades$user) {
    
    #Set denominator
    grades[grades$user == name, "denominator"] <- grades[grades$user == name, "denominator"] + 60
    
    #Add assignment grade
    if (name %in% df$user){
        grades[grades$user == name, as.character(df$date[1])] <- 
            round(df[df$user == name, "word_count"]/300, 2)*100
    } else {
        grades[grades$user == name, as.character(df$date[1])] <- 0
    }

    #Set numerator
    grades[grades$user == name, "numerator"] <- grades[grades$user == name, "numerator"] + 
                                                60*(grades[grades$user == name, as.character(df$date[1])]/100)
    #Re-calculate final grade
    grades[grades$user == name, "finalgrade"] <- round(grades[grades$user == name, "numerator"]/
                                                 grades[grades$user == name, "denominator"]*100, 0)
           
}

library(car)
grades[,as.character(df$date[1])] <- recode(grades[,as.character(df$date[1])], "100:999999 = 100")
grades$finalgrade <- recode(grades$finalgrade, "100:999999 = 100")
grades$finalletter <- recode(grades$finalgrade, "0:50 = 'F'; 51:60 = 'D';
                                                 61:70 = 'C'; 71:80 = 'B';
                                                 81:90 = 'A'; 91:100 = 'S'")

write.csv(grades, grade_file, row.names = F)

#Percentile rank all scores
df$word_count_z <- pnorm(scale(df$word_count))
if (any(is.nan(df$word_count_z))){df$word_count_z <- rep(.5, length(df$word_count_z))}
df$ave_word_len_z <- pnorm(scale(df$ave_word_len))
if (any(is.nan(df$ave_word_len_z))){df$ave_word_len_z <- rep(.5, length(df$word_count_z))}
df$longest_word_z <- pnorm(scale(df$longest_word))
if (any(is.nan(df$longest_word_z))){df$longest_word_z <- rep(.5, length(df$word_count_z))}
df$spell_check_z <- pnorm(scale(df$spell_check))
if (any(is.nan(df$spell_check))){df$spell_check <- rep(.5, length(df$word_count_z))}
df$grammar_check_z <- pnorm(scale(df$grammar_check))
if (any(is.nan(df$grammar_check))){df$grammar_check <- rep(.5, length(df$word_count_z))}

#Create normal distribution
dens <- density(rnorm(10000, mean = .5, sd = .15))
dist = data.frame(x = dens$x, y = dens$y)
dist$quant <- factor(findInterval(dist$y,
                     quantile(rnorm(10000, mean = .5, sd = .15),
                     prob=c(0, 0.25, 0.5, 0.75, 1))))
rm(dens)

### Test a few graphs
for (i in 1:nrow(df)){
    
    my_df <- df[i,]
    my_grades <- grades[grades$user == my_df$user,]
    
    my_filename = paste0(filename, "/reports/", my_df$user, "_report.html") 
    date = as.character(my_df$date)
    name = paste(grades[grades$user == my_df$user,"firstname"], 
                 grades[grades$user == my_df$user,"lastname"])

    #Build HTMLs
    rmarkdown::render(input = "report_template.Rmd", output_format = "html_document", 
                      params = list(name = name, date = date, my_df = my_df,
                                    my_grades = my_grades), output_file = my_filename)
    
    #Convert to pdf
    infile <- my_filename
    outfile <- paste0(substr(my_filename,1,nchar(my_filename)-5),'.pdf')
    comm<-paste("wkhtmltopdf", infile, outfile, sep = " ")
    system(comm)
    
    #Clear all variables
    rm(my_df)
}

#Remove all variables
rm(list=ls())
