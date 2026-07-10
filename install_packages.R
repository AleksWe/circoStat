message(">>> INSTALLER RPROFILE: ", Sys.getenv("R_PROFILE_USER"))
message(">>> INSTALLER LIBPATHS: ", paste(.libPaths(), collapse="; "))

lines <- readLines("../packages.txt")
pkgs <- sub("==.*", "", lines)
vers <- sub(".*==", "", lines)

options(repos = c(CRAN = "https://cloud.r-project.org"))
bioc_only <- c("Biostrings", "msa", "GenomeInfoDbData")

if (!requireNamespace("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

installed <- installed.packages(lib.loc = .libPaths()[1])

needs_install <- function(pkg, ver) {
    if (!pkg %in% rownames(installed)) return(TRUE)
    if (installed[pkg, "Version"] != ver) return(TRUE)
    return(FALSE)
}

to_install <- pkgs[sapply(seq_along(pkgs), function(i) needs_install(pkgs[i], vers[i]))]

if (length(to_install) == 0) {
    message(">>> All packages already installed correctly.")
    quit(save = "no")
}

message(">>> Installing: ", paste(to_install, collapse = ", "))

for (pkg in to_install) {

    if (pkg == "PopGenome") {
        message(">>> Installing PopGenome (archived)")
        install.packages(
            "https://cran.r-project.org/src/contrib/Archive/PopGenome/PopGenome_2.7.5.tar.gz",
            repos = NULL,
            type = "source"
        )
        next
    }

    if (pkg %in% bioc_only) {
        BiocManager::install(pkg, ask = FALSE)
        next
    }

    install.packages(pkg)
}

message(">>> Installation complete.")
