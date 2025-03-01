function fideSelector(onRowClick) {
  return {
    countries: [],
    players: [],
    selectedCountry: "",
    selectedFideId: "",
    playerSearch: "",
    loading: false,
    fetchTimeout: null,
    toastVisible: false,
    toastTimeout: null,
    sortKey: "fideid",
    sortAsc: true,
    nextUrl: null,
    previousUrl: null,
    pageStack: [],
    cache: {},

    // Fetch countries from the API
    fetchCountries() {
      fetch(
        "https://fide-players.fly.dev/players.json?sql=select+distinct%28country%29+from+players%3B"
      )
        .then((response) => response.json())
        .then((data) => {
          this.countries = data.rows.map((row) => row.country).sort();
          this.initializeFromUrl();
        });
    },

    // Initialize filters from URL
    initializeFromUrl() {
      const params = new URLSearchParams(window.location.search);
      if (params.has("country")) {
        this.selectedCountry = params.get("country");
      }
      if (params.has("search")) {
        this.playerSearch = params.get("search");
      }
      if (params.has("sort")) {
        this.sortKey = params.get("sort");
        this.sortAsc = params.get("order") !== "desc";
      }
      this.fetchPlayers();
    },

    // Throttled fetch players
    throttledFetchPlayers() {
      if (this.fetchTimeout) {
        clearTimeout(this.fetchTimeout);
      }

      // Save current state
      const currentSearch = this.playerSearch;
      const currentCountry = this.selectedCountry;

      this.fetchTimeout = setTimeout(() => {
        // Only fetch if the state hasn't changed again
        if (currentSearch === this.playerSearch && currentCountry === this.selectedCountry) {
          this.fetchPlayers();
        }
      }, 300);
    },

    // Convert URLs to HTTPS
    convertToHttps(url) {
      if (url && url.startsWith("http:")) {
        return url.replace("http://", "https://");
      }
      return url;
    },

    // Fetch players based on selected country and search text
    fetchPlayers(url = null) {
      this.loading = true;
      url = url || this.constructFetchUrl();
      this.pageStack.push(url);

      // Check cache
      if (this.cache[url]) {
        this.players = this.cache[url].players;
        this.nextUrl = this.cache[url].nextUrl;
        this.loading = false;

        // Prefetch next URL
        if (this.nextUrl && !this.cache[this.nextUrl]) {
          this.prefetchNextUrl(this.nextUrl);
        }
        return;
      }

      fetch(url)
        .then((response) => response.json())
        .then((data) => {
          this.players = data.rows;
          this.nextUrl = this.convertToHttps(data.next_url || null);
          this.cache[url] = { players: data.rows, nextUrl: this.nextUrl };
          this.loading = false;

          // Prefetch next URL
          if (this.nextUrl && !this.cache[this.nextUrl]) {
            this.prefetchNextUrl(this.nextUrl);
          }
        });
    },

    // Prefetch the next URL and cache the results
    prefetchNextUrl(nextUrl) {
      fetch(nextUrl)
        .then((response) => response.json())
        .then((data) => {
          this.cache[nextUrl] = {
            players: data.rows,
            nextUrl: this.convertToHttps(data.next_url),
          };
        });
    },

    // Construct the URL for fetching players
    constructFetchUrl() {
      let url = new URL("https://fide-players.fly.dev/players/players.json");
      url.searchParams.append("_size", 20); // Set page size to 20
      url.searchParams.append("_extra", "next_url");
      if (this.selectedCountry) {
        url.searchParams.append("country__exact", this.selectedCountry);
      }
      if (this.playerSearch) {
        url.searchParams.append("_search", this.playerSearch);
      }
      if (this.sortAsc) {
        url.searchParams.append("_sort", this.sortKey);
      } else {
        url.searchParams.append("_sort_desc", this.sortKey);
      }
      this.updateUrlParams();
      return url.toString();
    },

    // Reset the page stack
    resetPageStack() {
      this.pageStack = [];
      this.previousUrl = null;
      this.nextUrl = null;
      this.cache = {}; // Clear cache when filters are reset
    },

    // Select player and set the selected FIDE ID, copy to clipboard, and show toast
    selectPlayer(player) {
      this.selectedFideId = player.fideid;
      onRowClick(player);
    },

    // Copy FIDE ID to clipboard
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        console.log("FIDE ID copied to clipboard:", text);
      });
    },

    // Show toast notification
    showToast() {
      this.toastVisible = true;
      if (this.toastTimeout) {
        clearTimeout(this.toastTimeout);
      }
      this.toastTimeout = setTimeout(() => {
        this.toastVisible = false;
      }, 2000);
    },

    // Sort table by key
    sortTable(key) {
      this.resetPageStack();
      if (this.sortKey === key) {
        this.sortAsc = !this.sortAsc;
      } else {
        this.sortKey = key;
        this.sortAsc = true;
      }
      this.fetchPlayers(); // Fetch players with the new sort order
    },

    // Handle country change
    handleCountryChange() {
      this.resetPageStack();
      // Keep the existing search term when changing country
      this.fetchPlayers();
    },

    // Handle player search input
    handlePlayerSearchInput() {
      this.resetPageStack();
      // Keep the existing country selection when searching
      this.throttledFetchPlayers();
    },

    // Fetch next page
    fetchNext() {
      if (this.nextUrl) {
        this.fetchPlayers(this.nextUrl);
      }
    },

    // Fetch previous page
    fetchPrevious() {
      if (this.pageStack.length > 1) {
        this.pageStack.pop(); // Remove the current page URL
        const previousUrl = this.pageStack.pop(); // Get the previous page URL
        this.fetchPlayers(previousUrl);
      }
    },

    // Update URL parameters for shareability
    updateUrlParams() {
      const params = new URLSearchParams();
      if (this.selectedCountry) {
        params.set("country", this.selectedCountry);
      }
      if (this.playerSearch) {
        params.set("search", this.playerSearch);
      }
      params.set("sort", this.sortKey);
      params.set("order", this.sortAsc ? "asc" : "desc");
      history.replaceState(
        null,
        "",
        `${window.location.pathname}?${params.toString()}`
      );
    },
  };
}
