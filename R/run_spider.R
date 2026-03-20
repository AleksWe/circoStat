#' Perform Sliding Window Nucleotide Diagnostic Analysis
#'
#' This function reads a DNA alignment, assigns groups based on a provided 
#' sample table, and executes a sliding window analysis to identify 
#' diagnostic nucleotides.
#'
#' @param alignment_path String. The file path to the FASTA alignment.
#' @param samples_table Data frame. Must contain a \code{group} column mapping 
#'   each sequence to a category.
#' @param window_size Integer. The size of the sliding window (default: 500).
#' @param jump_size Integer. The step size between windows (default: 50).
#'
#' @return A Data frame containing the results of the \code{slideNucDiag} analysis.
#' @export
#'
#' @examples
#' # results <- run_spider("alignment.fasta", my_samples, window_size = 300)
run_spider <- function(alignment_path = "", samples_table = NULL, window_size = 500, jump_size = 50) {
  
  if (alignment_path == "" || !file.exists(alignment_path)) {
    stop("Error: The alignment file path is empty or the file does not exist.")
  }
  
  if (is.null(samples_table)) {
    stop("Error: 'samples_table' must be provided.")
  }
  
  if (!("group" %in% colnames(samples_table))) {
    stop("Error: 'samples_table' must contain a column named 'group'.")
  }
  
  dna <- ape::read.dna(alignment_path, format = "fasta")
  
  if (nrow(dna) != nrow(samples_table)) {
    stop(paste("Error: Mismatch between FASTA sequences (", nrow(dna), 
               ") and samples_table rows (", nrow(samples_table), ").", sep=""))
  }
  
  rownames(dna) <- samples_table$group
  
  nuc_div_list <- slideNucDiag(dna, rownames(dna), width = window_size, interval = jump_size)
  
  message("Analysis successful.")
  
  return(as.data.frame(nuc_div_list))
}