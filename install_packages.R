
options(repos = c(CRAN = "https://cloud.r-project.org"))

pkgs <- trimws(readLines("/circoStat/packages.txt"))

# Parse package names and versions
parse_pkgs <- function(prefix) {
    x <- sub(
        paste0("^", prefix, ":"),
        "",
        grep(paste0("^", prefix, ":"), pkgs, value = TRUE)
    )

    parts <- strsplit(x, "==", fixed = TRUE)

    data.frame(
        package = vapply(parts, `[[`, character(1), 1L),
        version = vapply(parts, function(x) {
            if (length(x) > 1L) x[2L] else NA_character_
        }, character(1))
    )
}

cran <- parse_pkgs("CRAN")
bio  <- parse_pkgs("BIOC")

# ---------------------------------
# CRAN packages: install exact versions
# ---------------------------------

message(">>> Installing CRAN packages")

if (nrow(cran)) {
    if (!requireNamespace("remotes", quietly = TRUE))
        install.packages("remotes")

    for (i in seq_len(nrow(cran))) {
        message(">>> Installing ", cran$package[i],
                " version ", cran$version[i])

        remotes::install_version(
            cran$package[i],
            version = cran$version[i],
            repos = "https://cloud.r-project.org",
            dependencies = c("Depends", "Imports", "LinkingTo"),
            upgrade = "never",
        )
    }
}

# ---------------------------------
# Bioconductor 3.20 (R 4.4)
# ---------------------------------

message(">>> Configuring Bioconductor 3.20")

if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")

options(repos = BiocManager::repositories(version = "3.20"))

BiocManager::install(
    version = "3.20",
    ask = FALSE,
    update = FALSE
)

stopifnot(as.character(BiocManager::version()) == "3.20")

# Install all requested Bioconductor packages together
message(">>> Installing Bioconductor packages")

if (nrow(bio)) {
    BiocManager::install(
        bio$package,
        ask = FALSE,
        update = FALSE
    )
}

# ---------------------------------
# Archived PopGenome
# ---------------------------------

message(">>> Installing PopGenome")

install.packages(
    "https://cran.r-project.org/src/contrib/Archive/PopGenome/PopGenome_2.7.5.tar.gz",
    repos = NULL,
    type = "source"
)

# ---------------------------------
# Verify all requested package versions
# ---------------------------------

message(">>> Verifying package versions")

requested <- rbind(cran, bio)
installed <- utils::installed.packages()

actual <- installed[
    match(requested$package, installed[, "Package"]),
    "Version"
]

check <- data.frame(
    Package = requested$package,
    Requested = requested$version,
    Installed = actual
)

print(check, row.names = FALSE)

bad <- is.na(actual) |
    (!is.na(requested$version) & actual != requested$version)

if (any(bad)) {
    stop("PACKAGE VERSION MISMATCH - Docker build stopped!")
}

message(">>> ALL PACKAGE VERSIONS VERIFIED <<<")
