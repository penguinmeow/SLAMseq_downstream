#!/usr/bin/env Rscript

## 0 configure the inputs
indir <- "/research/rgs01/project_space/yu3grp/Network_JY/yu3grp/LAP_Green/190553SLAMseq/output/" # dir of Slamseq Outputs
#replace with "/Volumes/project_space/yu3grp/Network_JY/yu3grp/LAP_Green/190553SLAMseq/output/" when running in workstation.

outdir <- "/research/rgs01/project_space/yu3grp/Network_JY/yu3grp/LAP_Green/190553SLAMseq/output/netbid" # dir for Summary, including Correlation and Master Tables
samples <- read.table("sample.txt",col.names = "series")
sample[,"directory"] <- paste0(indir,sample$series,"_R1/count")
samples <- as.character(sample$series)
directories <- as.character(sample$directory)
head(directories)
cat("The input information has been read!\n")

## 1 collect expression information


# extract quantification information
cat("The quantification results are being collected...\n")
files <- lapply(directories, list.files, pattern=".tsv", full.names = TRUE)

# create data frames
name <- c("Chromosome", "Start", "End", "Name" ,"Length" ,"Strand", "ConversionRate", "ReadsCPM", "Tcontent", "CoverageOnTs" , "ConversionsOnTs", "ReadCount" , 
          "TcReadCount", "multimapCount" , "ConvRateLower", "ConvRateUpper")
master_table <- lapply(files[1:length(samples)], function(x) read.table(x,header = TRUE, col.names = name))
class(master_table)
names(master_table) <- samples

#Using Reduce to merge multiple data frames
masterTable<- Reduce(function(x,y,...) merge(x,y, by = "Name", ...), master_table)
                               
#adding rowname
row.names(masterTable) <- masterTable$Name
masterTable <- masterTable[, -1]                   

cat("The quantification information have been collected!\n")

## 2 prepare and print expression matrix
variables <- as.character(read.delim("variables.txt")[,1])
for(i in seq_along(variables)) {
  matrix <- masterTable[,grepl(variables[[i]], names(masterTable))]
  names(matrix) <- samples
  matrix <- matrix[rowSums(matrix) > 0, ]
  matrix.print <- data.frame(row.names(matrix), Gene_ID = row.names(matrix), matrix)
  write.table(matrix.print, file = paste0(outdir,"/",variables[[i]],".txt"), quote = F, sep = "\t", row.names = F, col.names = T)
}
cat("The expression master tables have been created and printed!\n")
