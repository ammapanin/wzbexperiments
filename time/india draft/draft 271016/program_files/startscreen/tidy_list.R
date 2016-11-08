
# Created: ; Last updated:

library(dplyr)

id.folder <- file.path("/Users/aserwaahWZB/Projects/GUI Code",
                       "time/india draft/draft 271016/program_files",
                       "startscreen/identifiers")
hh.file.name <- "household_listing_"
fbase.path <- file.path(id.folder,
                       paste0(hh.file.name, "081116_base.csv"))
hh <- tbl_df(read.csv(fbase.path, sep = ";", stringsAsFactors = FALSE))

akkur <-  filter(hh, vid == 25) %>%
    mutate(wzb.hh.id =  paste0(tid, vid,
               sprintf("%03d", seq_along(akkur$village))),
           wzb.ind.id = as.character(paste0(wzb.hh.id, "x1")),
           experiment_name = name,
           comparison_task = 1)

hh[hh$vid == 25, ] <- akkur


fout.path <- file.path(id.folder,
                       paste0(hh.file.name, "081116.csv"))
write.csv(hh, fout.path, row.names = FALSE)
