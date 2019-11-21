#Import Libraries
suppressMessages(library(tidyr))
suppressMessages(library(dplyr))

#Accept arguments from python script
args = paste0("grade_model_training/output/results_layer_7.csv")#, commandArgs(trailingOnly=TRUE), ".csv")
#args = paste0("output/psynary_", "depmedwin2_4", ".csv") #For testing

#Load data
df <- read.csv(args, header = T, stringsAsFactors = F)

#Reformat to long data
ldf <- df[,c("mean_squared_error", "val_mean_squared_error", "mean_absolute_error",
             "val_mean_absolute_error", "mean_absolute_percentage_error", 
             "val_mean_absolute_percentage_error", "dense_one", "dense_two",
             "dense_three", "lr", "optimizer", "batch_size")]
ldf <- gather(ldf, key = train_test, value = error, -dense_one, -dense_two,
              -dense_three, -lr, -optimizer, -batch_size)

#Recode train/test
ldf$train_test <- as.factor(recode(ldf$train_test,
                            "categorical_accuracy" = "Training Data",
                            "val_categorical_accuracy" = "Test Data"))
ldf$train_test <- relevel(ldf$train_test, ref = "Training Data")

#Recode optimizers
ldf$optimizer <- recode(ldf$optimizer, "<class 'keras.optimizers.Nadam'>" = "Nadam",
                                       "<class 'keras.optimizers.Adam'>" = "Adam",
                                       "<class 'keras.optimizers.RMSprop'>" = "RMSprop",
                                       "<class 'keras.optimizers.SGD'>" = "SGD")

#Finish long format
ldf <- gather(ldf, key = parameter, value = setting, -train_test, -error)

#Rename parameters
ldf$parameter <- recode(ldf$parameter, "batch_size" = "Batch Size",
                                       "dense_one" = "Dense Neuron 1",
                                       "dense_two" = "Dense Neuron 2",
                                       "dense_three" = "Dense Neuron 3",
                                       "lr" = "Learning Rate",
                                       "optimizer" = "Optimizer")

#Leading zeros
longest_str <- max(nchar(ldf[ldf$parameter != "Optimizer", "setting"]))
longest_str <- paste0("%0", as.character(longest_str), "s")
ldf$setting <- sprintf(longest_str, ldf$setting)

#Grpah title
title <- sub("^([^.]*).*", "\\1", basename(args))

#Render HTML version of report
infile <- paste0(sub("^([^.]*).*", "\\1", args), ".html")
rmarkdown::render(input = 'grade_model_training/datahelpers/result_template.Rmd', 
                  output_format = "html_document", 
                  output_file = infile,
                  params = c(ldf = ldf, title = title),
                  quiet = T)

#Convert to pdf
outfile <- paste0(sub("^([^.]*).*", "\\1", args), ".pdf")
comm<-paste("wkhtmltopdf -O landscape -q ", infile, outfile, sep = " ")
system(comm)

#Cleanup
unlink(infile)
unlink(paste0(sub("^([^.]*).*", "\\1", args), "_files"), recursive=TRUE)
rm(args, title, df, ldf, longest_str, infile, outfile, comm)
