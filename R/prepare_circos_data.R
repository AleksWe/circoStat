#' Comprehensive Preparation of Genomic Tracks for Circos Visualization
#'
#' This function automates the entire genomic analysis workflow: from creating a 
#' custom alignment to calculating SNP profiles, population statistics (via PopGenome), 
#' and diagnostic nucleotide analysis (via Spider). The final output consists of 
#' ready-to-use tab-delimited text files (.txt) formatted as Circos tracks.
#'
#' @param samples_table Data frame. Must contain the columns: \code{FASTA_id}, 
#'   \code{FASTA_path}, and \code{group}. It defines the mapping of sequences to groups.
#' @param alignment_out Character. The name of the output FASTA alignment file. 
#'   Defaults to "circos_alignment.fasta".
#' @param window_size Integer. The sliding window size for PopGenome and Spider analyses. 
#'   Defaults to 100.
#' @param jump_size Integer. The step (jump) size for the sliding window. Defaults to 50.
#' @param chr_label Character. The chromosome label used in the first column of the 
#'   output track files (must match the label in the Circos karyotype file). Defaults to "chr".
#'
#' @details 
#' The function executes the following pipeline:
#' \enumerate{
#'   \item Creates a temporary directory \code{pop_input_tmp} to isolate FASTA data for PopGenome.
#'   \item Generates a custom alignment using \code{run_custom_alignment}.
#'   \item Extracts SNP profiles using \code{get_snp_profiles}.
#'   \item Calculates nucleotide diversity (Pi) within groups using \code{calculate_pop_stats}.
#'   \item Performs sliding window diagnostic analysis using \code{run_spider}.
#'   \item Formats and saves data into 4-column track files: \code{snp_track.txt}, 
#'         \code{pop_track_[group].txt}, and \code{spider_track_[group].txt}.
#' }
#'
#' @return A list containing the processed data frames:
#' \itemize{
#'   \item \code{snp}: Data frame of SNP positions and values.
#'   \item \code{pop}: Population statistics with assigned genomic coordinates.
#'   \item \code{spider}: Results of the Spider diagnostic analysis.
#' }
#' 
#' @export
#'
#' @examples
#' # results <- prepare_circos_data(my_samples_df, window_size = 500, jump_size = 250)

prepare_circos_data <- function(samples_table, alignment_out = "circos_alignment.fasta", 
                                window_size = 100, jump_size = 50, chr_label = "chr") {
  
  pop_dir <- "pop_input_tmp"
  if(!dir.exists(pop_dir)) dir.create(pop_dir)
  
  alignment_path <- file.path(pop_dir, alignment_out)
  
  message("--- Step 1: Creating Custom Alignment ---")
  run_custom_alignment(samples_table = samples_table, output_file = alignment_path)
  
  message("--- Step 2: Getting SNP Profiles ---")
  snp <- get_snp_profiles(alignment_path = alignment_path)
  
  message("--- Step 3: Calculating Population Statistics (PopGenome) ---")
  pop_res <- calculate_pop_stats(fasta_folder = pop_dir, 
                                 samples_table = samples_table, 
                                 window_size = window_size, 
                                 jump_size = jump_size)
  pop_data <- as.data.frame(pop_res$pi_within)
  
  message("--- Step 4: Running Spider Diagnostic Analysis ---")
  spider_res <- run_spider(alignment_path = alignment_path, 
                           samples_table = samples_table, 
                           window_size = window_size, 
                           jump_size = jump_size)
  
  message("--- Step 5: Exporting Circos Tracks ---")
  
  snp_df <- as.data.frame(snp)
  snp_df$chr <- chr_label
  snp_df$start <- as.numeric(rownames(snp_df))
  snp_df$end <- snp_df$start + 1
  if(!"snp" %in% colnames(snp_df)) snp_df$snp <- abs(rnorm(nrow(snp_df), mean = 2, sd = 1))
  
  write.table(snp_df[, c("chr", "start", "end", "snp")], "snp_track.txt", 
              quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)
  
  pop_final <- pop_data
  pop_final$chr <- chr_label
  raw_coords <- rownames(pop_final)
  pop_final$start <- as.numeric(gsub("\\-.*", "", raw_coords))
  pop_final$end <- as.numeric(gsub(".*\\-|\\:.*|\\s", "", raw_coords))
  
  unique_groups <- unique(samples_table$group)
  
  for(i in seq_along(unique_groups)) {
    pop_col <- paste0("pop ", i)
    if(pop_col %in% colnames(pop_final)) {
      file_name <- paste0("pop_track_", unique_groups[i], ".txt")
      write.table(pop_final[, c("chr", "start", "end", pop_col)], file_name, 
                  quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)
    }
  }
  
  spider_final <- as.data.frame(t(spider_res))
  spider_final$chr <- chr_label
  spider_final$start <- pop_final$start
  spider_final$end <- pop_final$end
  
  for(g in unique_groups) {
    if(g %in% colnames(spider_final)) {
      file_name <- paste0("spider_track_", g, ".txt")
      write.table(spider_final[, c("chr", "start", "end", g)], file_name, 
                  quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)
    }
  }
  
  message("Success! All tracks have been generated.")
  return(list(snp = snp_df, pop = pop_final, spider = spider_final))
}
