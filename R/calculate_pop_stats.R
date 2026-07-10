#' Calculate Sliding Window Population Statistics
#'
#' This function performs genomic scans using PopGenome, calculating FST, 
#' nucleotide diversity (Pi), and absolute divergence (Dxy) across sliding windows. 
#' Results are normalized by window size.
#'
#' @param fasta_folder Character; path to the folder containing FASTA files.
#' @param samples_table Data frame with 'FASTA_id' and 'group' columns.
#' @param window_size Integer; width of the sliding window in base pairs (default: 500).
#' @param jump_size Integer; step size between windows (default: 100).
#'
#' @return A list containing:
#'   \item{pi_within}{Normalized nucleotide diversity within each population.}
#'   \item{fst}{FST values (fixation index) between populations.}
#'   \item{dxy}{Normalized absolute divergence (Dxy) between populations.}
#'   \item{windows}{Names/Coordinates of the sliding windows.}
#'
#' @importFrom PopGenome readData get.individuals set.populations sliding.window.transform F_ST.stats diversity.stats get.F_ST
#' @export

calculate_pop_stats <- function(fasta_folder, 
                                samples_table, 
                                window_size = 500, 
                                jump_size = 100) {
  
  message("Loading FASTA data from: ", fasta_folder)
  GENOME.class <- PopGenome::readData(fasta_folder, format = "FASTA")
  
  actual_ids <- PopGenome::get.individuals(GENOME.class)[[1]]

  pop_list <- split(samples_table$FASTA_id, samples_table$group)
  pop_list <- lapply(pop_list, function(x) x[x %in% actual_ids])

  valid_pops <- sapply(pop_list, length) >= 2
  if (!any(valid_pops)) {
    stop("Error: No populations found with at least 2 matching individuals in the FASTA files.")
  }

  if (sum(valid_pops) < length(pop_list)) {
    warning("Some populations were excluded due to having < 2 individuals: ", 
            paste(names(pop_list)[!valid_pops], collapse = ", "))
  }
  
  pop_list <- pop_list[valid_pops]
  GENOME.class <- PopGenome::set.populations(GENOME.class, pop_list)

  message("Transforming into sliding windows (size: ", window_size, ", jump: ", jump_size, ")...")
  GENOME.class.slide <- PopGenome::sliding.window.transform(
    GENOME.class, 
    width = window_size, 
    jump = jump_size, 
    type = 2, 
    whole.data = TRUE
  )

  message("Calculating Population Genetics Statistics (this may take a while)...")
  GENOME.class.slide <- PopGenome::F_ST.stats(GENOME.class.slide, detail = TRUE)
  GENOME.class.slide <- PopGenome::diversity.stats(GENOME.class.slide, pi = TRUE)
  
  pi_within_raw <- GENOME.class.slide@nuc.diversity.within
  
  if (is.null(pi_within_raw) || length(pi_within_raw) == 0) {
    warning("Calculations returned empty results. Check for lack of SNPs or missing data.")
    return(NULL)
  }
  
  pi_within <- pi_within_raw / window_size
  
  fst_values <- PopGenome::get.F_ST(GENOME.class.slide)
  
  dxy_raw <- GENOME.class.slide@nuc.diversity.between
  dxy_values <- dxy_raw / window_size
  
  win_names <- GENOME.class.slide@region.names

  rownames(pi_within) <- win_names
  
  if (is.matrix(fst_values)) {
    if (nrow(fst_values) == length(win_names)) rownames(fst_values) <- win_names
  }
  
  if (is.matrix(dxy_values)) {
    if (nrow(dxy_values) == length(win_names)) rownames(dxy_values) <- win_names
    colnames(dxy_values) <- paste0("Dxy_", colnames(dxy_values))
  }
  
  results_list <- list(
    pi_within = pi_within,
    fst = fst_values,
    dxy = dxy_values,
    windows = win_names
  )
  
  message("Analysis successful.")
  return(results_list)
}
