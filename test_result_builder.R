#Recieve filename
args = commandArgs(trailingOnly=TRUE)

#Ensure at least one argument
if (length(args)!=2) {
    stop(paste0("Directory name required.",length(args)),
         call.=FALSE)
}

#To test script
#args = c("hyogenACE_2019","process_essay")

#Read file
filename = paste0("output/",args[1],"/",args[2],"/",args[2],".csv")
df = read.csv(filename, header = T)[,c(1,3:11)]

#Recode data
suppressMessages(library(car))
df$revision = recode(df$revision, "'pre'='Before'; 'post' = 'After'")
df$revision = relevel(df$revision, ref = "Before")
df$passive_voice = df$passive_voice
df$sentence_length = df$sentence_length

#Reshape data
suppressMessages(library(tidyr))
df$word_count <- NULL
df <- df %>% gather(domain, Score, word_choice:grade)
df$domain <- as.factor(df$domain)
levels(df$domain) <- c("Grade","Passive Voice","Sentence Length","Simple Starts",
                       "Transition Phrases","Vocabulary","Word Choice")
df$domain <- as.character(df$domain)
df$user <- gsub(paste0("_",args[2]), "", as.character(df$name))

#Segmentation dataframe
df$letter <-NULL
seg_df <- df %>% spread(revision, Score)

#Add color
color_map <- c()
for (i in 1:nrow(seg_df)){
    if (seg_df$domain == "Passive Voice"){
        if(seg_df$Before < seg_df$After){
            color_map = append(color_map, "red")
        } else {
            color_map = append(color_map, "green")
        }
    } else {
        if(seg_df$Before > seg_df$After){
            color_map = append(color_map, "red")
        } else {
            color_map = append(color_map, "green")
        }
    }
}
seg_df$color_map <- color_map

#Update grade book
grade_file <- paste0('resources/',args[1],"_grades.csv")
grades = read.csv(grade_file, header = T)
grades[,args[2]] <-rep(0,nrow(grades))

for(name in unique(df$user)){
    
    improvement = abs(round(df[df$user == name & df$revision == "After" & df$domain == "Grade", "Score"]-
                        df[df$user == name & df$revision == "Before" & df$domain == "Grade", "Score"],0))
    
    #Give no bonus to students who did not turn in a draft
    if (improvement > 30){
        improvement = 0
    }
    
    grades[grades$user == name, args[2]] <- 
        df[df$user == name & df$revision == "After" & df$domain == "Grade", "Score"] + improvement
    grades[grades$user == name, "denominator"] <- grades[grades$user == name, "denominator"] + 100
    grades[grades$user == name, "numerator"] <- grades[grades$user == name, "numerator"] + 
                                                grades[grades$user == name, args[2]]
    grades[grades$user == name, "finalgrade"] <- round(grades[grades$user == name, "numerator"]/
                                                 grades[grades$user == name, "denominator"]*100,0)
}

grades[,args[2]] <- recode(grades[,args[2]], "100:999999 = 100")
grades$finalgrade <- recode(grades$finalgrade, "100:999999 = 100")
grades$finalletter <- recode(grades$finalgrade, "0:50 = 'F'; 51:60 = 'D';
                                                 61:70 = 'C'; 71:80 = 'B';
                                                 81:90 = 'A'; 91:100 = 'S'")

#Save to gradebook
write.csv(grades, grade_file, row.names = F)

#Remove unecessary variables
rm(color_map,filename,i,name)

### Test a few graphs
for (i in as.character(unique(df$user))){
    
    #Individual datafiles
    my_seg_df <- seg_df[seg_df$user == i,]
    my_df <- df[df$user == i,]
    my_grades <- grades[grades$user == i,]

    #Text-based data
    project_name <- args[2]
    my_filename = paste0("output/",args[1],"/",args[2],"/post_reports/", my_df$user[1],"_final_report.html") 
    date = Sys.Date()
    name = paste(grades[grades$user == i,"firstname"], 
                 grades[grades$user == i,"lastname"])
    
    #Build HTMLs
    rmarkdown::render(input = "test_report_template.Rmd", output_format = "html_document", 
                      params = list(name = name, date = date, df = df, my_df = my_df,
                                    my_seg_df = my_seg_df, my_grades = my_grades, 
                                    project_name = project_name), output_file = my_filename)

    #Convert to pdf
    infile <- my_filename
    outfile <- paste0(substr(my_filename,1,nchar(my_filename)-5),'.pdf')
    comm<-paste("wkhtmltopdf", infile, outfile, sep = " ")
    system(comm)
    
    #Clear individual variables
    rm(my_df,my_grades,i,my_filename,name,comm,date,infile,outfile,project_name)
}

#Remove all variables
rm(list=ls())

