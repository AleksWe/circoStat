## Diagnostic nucleotides for Rubia, Galium, and Leptodermis with spider package
# Loading data
#setwd("C:/Users/Ania/Desktop/rzeczyKamila/alignment/")
#install.packages('ape', repos = "http://cran.us.r-project.org")

#my_packages <- c("ape", "spider")                                        # Specify your packages
#not_installed <- my_packages[!(my_packages %in% installed.packages()[ , "Package"])]    # Extract not installed packages
#if(length(not_installed)) install.packages(not_installed, repos ='https://cran.rstudio.com/')

library(ape)
library(spider)

### Rubia alignment
dat_rub <- read.dna("Rubia_align.fasta", format = "fasta")
dimnames(dat_rub)[[1]] <- c("Rubia_yunnanensis", "Rubia_podantha", "Rubia_cordifolia")
dimnames(dat_rub)[[1]]

### Galium alignment
dat_gal <- read.dna("Galium_align.fasta", format = "fasta")
dimnames(dat_gal)[[1]] <- c("Galium_boreale", "Galium_trifidum-glu125", "Galium_trifidum-glua2", "Galium_palustre-31-2",
                            "Galium_palustre-31-8", "Galium_mollugo", "Galium_verum", "Galium_spurium", "Galium_aparine", "Galium_odoratum")
dimnames(dat_gal)[[1]]

### Leptodermis alignment
#dat_lep <- read.dna("Leptodermis_align.fasta", format = "fasta")
#dimnames(dat_lep)[[1]] <- c("Leptodermis_oblonga", "Leptodermis_forrestii", "Leptodermis_ludlowii", "Leptodermis_scabrida_2", "Leptodermis_gracilis",
#                            "Leptodermis_scabrida_1", "Leptodermis_kumaonensis", "Leptodermis_hirsutiflora_2", "Leptodermis_hirsutiflora_1")
#dimnames(dat_lep)[[1]]
#
# Creating a genus vector
### Rubia
RubGen <- strsplit(dimnames(dat_rub)[[1]], split = "_")
RubGen <- sapply(RubGen, function(x) paste(x[1], sep = "_"))
RubGen

### Galium
GalGen <- strsplit(dimnames(dat_gal)[[1]], split = "_")
GalGen <- sapply(GalGen, function(x) paste(x[1], sep = "_"))
GalGen

### leptodermis
#LepGen <- strsplit(dimnames(dat_lep)[[1]], split = "_")
#LepGen <- sapply(LepGen, function(x) paste(x[1], sep = "_"))
#LepGen

# Calculating diagnostic nucleotides
### Rubia
RubslidNC1 <- slideNucDiag(dat_rub, RubGen, width = 500, interval = 100)

### Galium
GalslidNC1 <- slideNucDiag(dat_gal, GalGen, width = 500, interval = 100)
# max(colSums(GalslidNC1))
### Leptodermis
# LepslidNC1 <- slideNucDiag(dat_lep, LepGen, width = 500, interval = 100)

# Creating a table with diagnostic nucleotides and saving files
### we need position of nucleotides and one slideAnalyses is enough
GalAna <- slideAnalyses(dat_gal, GalGen, width=500, interval=100,
                        distMeasures=TRUE, treeMeasures=TRUE)

### table of diagnostic nucleotides
tab_slidND <- data.frame(position = GalAna$pos_out, Rubia = RubslidNC1[1,], Galium = GalslidNC1[1,]) #Leptodermis = LepslidNC1[1,])
tab_slidND <- data.frame(position = GalAna$pos_out, Galium = GalslidNC1[1,])

### additional columns galiumchr needed for a circosplot
tab_slidND$chrom <- "galiumchr"
tab_slidND$position_end <- ""
for (i in 1:nrow(tab_slidND)) {
  if (i != nrow(tab_slidND)) {
    tab_slidND[i,]$position_end <- tab_slidND[i+1,]$position  
  }else{
    tab_slidND[i,]$position_end <- 139905
  }
}

tab_slidND$Galium <- round(tab_slidND$Galium / 8)

### saving
#write.table(tab_slidND[,c("chrom", "position", "position_end", "Rubia")], "Rub_tab_slidND.txt", quote = F, row.names = F, col.names = F)
write.table(tab_slidND[,c("chrom", "position", "position_end", "Galium")], "Gal_tab_slidND.txt", quote = F, row.names = F, col.names = F)
#write.table(tab_slidND[,c("chrom", "position", "position_end", "Leptodermis")], "Lep_tab_slidND.txt", quote = F, row.names = F, col.names = F)

### dividing diagnostic nucleotides by species number

#Rubia <- read.table("Rub_tab_slidND.txt")
Galium <- read.table("Gal_tab_slidND.txt")
#Lepto <- read.table("Lep_tab_slidND.txt")

#Rubia$V4 <- round(Rubia$V4/3)
Galium$V4 <- round(Galium$V4/8)
#Lepto$V4 <- round(Lepto$V4/7)

### saving again
#write.table(Rubia[,c(1,2,3,4)], "Rubia_divided.txt", quote = F, row.names = F, col.names = F)
write.table(Galium[,c(1,2,3,4)], "Gal_divided.txt", quote = F, row.names = F, col.names = F)
#write.table(Lepto[,c(1,2,3,4)], "Lep_divided.txt", quote = F, row.names = F, col.names = F)
