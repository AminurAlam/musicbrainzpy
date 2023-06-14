#![warn(deprecated_in_future)]
#![warn(future_incompatible)]
#![warn(nonstandard_style)]
#![warn(rust_2018_compatibility)]
#![warn(rust_2018_idioms)]
#![warn(trivial_casts, trivial_numeric_casts)]
// #![warn(unused)]

use clap::Parser;

#[derive(Parser)]
#[command(author = "AminurAlam")]
#[command(version = "2.0.0")]
#[command(about = "Musicbrainz artwork downloader", long_about = None)]
struct Cli {
    /// name of the album
    query: String,

    /// limit the number of results displayed
    #[arg(short, long, value_name = "NUM")]
    #[arg(default_value_t = 5 )]
    limit: u8,

    /// change the output directory where files are saved
    #[arg(short, long, value_name = "DIR")]
    #[arg(default_value_t = ("Covers/").to_string() )]
    output: String,

    /// filter the type of images saved
    #[arg(short = 'i', long, value_name = "TYPE")]
    #[arg(default_value_t = ("front").to_string() )]
    filter_image: String,

    /// filter search results
    #[arg(short = 's', long, value_name = "TYPE")]
    #[arg(default_value_t = ("all").to_string() )]
    filter_search: String,

    /// filter images by filesize (in kb)
    #[arg(short = 'b', long, value_name = "TYPE")]
    #[arg(default_value_t = 200 )]
    filter_size: u8,
}

// def search_rg(query: str) -> dict:
//     rgs: list[dict] = api.search("release-group", query, args.limit, 0)['release-groups']
//
//     if args.search != "all":  # filtering the search results by --filter-search
//         rgs = list(filter(lambda rg: rg.get('primary-type', '').lower() == args.search, rgs))
//
//     if not rgs:
//         raise Exception("no search results. try changing filter, increasing limit")
//
//     rgs.sort(reverse=True, key=lambda rg: rg['score'] * len(rg['releases']))
//
//     for n, rg in enumerate(rgs, start=1):
//         artists: str = ", ".join([name['name'] for name in rg['artist-credit']])
//         types: str = ", ".join([rg.get('primary-type', 'none')] + rg.get('secondary-types', []))
//         print(f"[{ylw}{n}{wht}] {grn}{artists} - {rg.get('title')}{wht} ({rg['count']} {types})")
//
//     choice: str = input("\n>choose release-group: ")
//     choice == "0" and exit()
//     print('\x1b[1A\x1b[2K' * (len(rgs) + 2))  # clearing screen/search results
//
//     return rgs[0] if choice == "" else rgs[int(choice) - 1]


fn search_rg(query: String) {
    unimplemented!();
}

fn main() {
    let mbz_root_url = "https://musicbrainz.org/ws/2";
    let caa_root_url = "https://coverartarchive.org";
    let ia_root_url = "https://archive.org/download";
    let cli = Cli::parse();

    search_rg(cli.query)

    // You can check the value provided by positional arguments, or option arguments
    // println!("Value for name: {}", cli.query);
}
