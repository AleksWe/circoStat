# Read package list
lines <- readLines("packages.txt")

# Split into name + version
pkgs <- sub("==.*", "", lines)
vers <- sub(".*==", "", lines)

# Set CRAN mirror
options(repos = c(CRAN = "https://cloud.r-project.org"))

# Ensure BiocManager is available
if (!requireNamespace("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

# Bioconductor-only packages (force install via BiocManager)
bioc_only <- c("Biostrings", "msa", "GenomeInfoDbData")

for (i in seq_along(pkgs)) {
  pkg <- pkgs[i]
  ver <- vers[i]

  message("Installing ", pkg, " @ ", ver)

  if (pkg %in% bioc_only) {
    # Always install these from Bioconductor
    BiocManager::install(pkg, ask = FALSE)
  } else {
    # CRAN package with version pinning
    install.packages(pkg, version = ver)
  }
}
