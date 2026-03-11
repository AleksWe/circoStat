#' Perform Multiple Sequence Alignment from External Files
#'
#' This function reads FASTA files based on paths provided in a data frame, 
#' renames the sequences using provided identifiers, performs multiple 
#' sequence alignment (MSA), and exports the result to a file.
#'
#' @param samples_table A data frame containing at least two columns: 
#'   \code{FASTA_path} (character, absolute or relative paths to .fasta files) 
#'   and \code{FASTA_id} (character, the desired names for the sequences).
#' @param output_file Character; the name/path of the output FASTA file 
#'   (defaults to "Alignment.fasta").
#' @param method Character; the alignment algorithm to use. Options are 
#'   "ClustalW" (default), "ClustalOmega", or "Muscle".
#'
#' @return Invisibility returns an object of class \code{MsaDNAMultipleAlignment}. 
#'   As a side effect, it writes a FASTA file to the disk.
#'
#' @importFrom Biostrings readDNAStringSet writeXStringSet
#' @importFrom msa msa
#' @importFrom methods as
#' @export
#' @example test <- run_custom_alignment(samples_table = samples_table,
#'                            output_file = "Alignment.fasta",
#'                             method = "ClustalW")


run_custom_alignment <- function(samples_table, 
                                 output_file = "Alignment.fasta", 
                                 method = "ClustalW") {
  
  if (!all(c("FASTA_path", "FASTA_id") %in% colnames(samples_table))) {
    stop("The 'samples_table' must contain 'FASTA_path' and 'FASTA_id' columns.")
  }
  
  if (!all(file.exists(samples_table$FASTA_path))) {
    missing_files <- samples_table$FASTA_path[!file.exists(samples_table$FASTA_path)]
    stop("The following files were not found: ", paste(missing_files, collapse = ", "))
  }

  message("Reading sequences from ", nrow(samples_table), " files...")
  list_of_seqs <- lapply(samples_table$FASTA_path, Biostrings::readDNAStringSet)

  for (i in seq_along(list_of_seqs)) {
    names(list_of_seqs[[i]]) <- samples_table$FASTA_id[i]
  }

  combined_to_align <- do.call(c, list_of_seqs)

  message("Starting alignment using method: ", method, "...")
  my_alignment <- msa::msa(combined_to_align, method = method)

  alignment_set <- methods::as(my_alignment, "BStringSet")
  Biostrings::writeXStringSet(alignment_set, file = output_file)
  
  message("Success! Alignment saved to: ", output_file)
  
  return(invisible(my_alignment))
}