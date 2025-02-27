<script>
  import { onMount } from "svelte";
  import { Link, useParams } from "svelte-navigator";
  import { articleService, feedService } from "../services/api";
  import { format } from "date-fns";

  const params = useParams();

  let articles = [];
  let feed = null;
  let loading = true;
  let error = null;
  let page = 1;
  let hasMore = true;
  let unreadOnly = false;

  onMount(async () => {
    await loadFeed();
    await loadArticles();
  });

  async function loadFeed() {
    try {
      feed = await feedService.getById($params.id);
    } catch (err) {
      error = err.message || "Failed to load feed details";
    }
  }

  async function loadArticles(reset = false) {
    loading = true;

    if (reset) {
      page = 1;
      articles = [];
    }

    try {
      const newArticles = await articleService.getAll({
        feed_id: $params.id,
        page,
        per_page: 20,
        unread_only: unreadOnly,
      });

      if (newArticles.length < 20) {
        hasMore = false;
      }

      articles = reset ? newArticles : [...articles, ...newArticles];
      loading = false;
    } catch (err) {
      error = err.message || "Failed to load articles";
      loading = false;
    }
  }

  async function loadMore() {
    if (loading || !hasMore) return;

    page += 1;
    await loadArticles();
  }

  async function refreshFeed() {
    try {
      loading = true;
      await feedService.refresh($params.id);
      await loadArticles(true);
    } catch (err) {
      error = err.message || "Failed to refresh feed";
      loading = false;
    }
  }

  async function toggleReadStatus(article, read) {
    try {
      await articleService.markAsRead(article.id, read);

      // Update the article in the list
      const index = articles.findIndex((a) => a.id === article.id);
      if (index !== -1) {
        articles[index].read = read;
        articles = [...articles]; // Trigger reactivity
      }
    } catch (err) {
      console.error("Failed to update read status:", err);
    }
  }

  function formatDate(dateString) {
    if (!dateString) return "Unknown date";

    try {
      const date = new Date(dateString);
      return format(date, "MMM d, yyyy h:mm a");
    } catch (err) {
      return "Invalid date";
    }
  }

  function toggleUnreadFilter() {
    unreadOnly = !unreadOnly;
    loadArticles(true);
  }
</script>

<div class="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
  {#if feed}
    <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
      <div>
        <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
          {feed.title}
        </h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
          {feed.description || "No description available"}
        </p>
      </div>
      <div class="flex space-x-3">
        <button
          class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
          on:click={toggleUnreadFilter}
        >
          {unreadOnly ? "show all" : "show unread only"}
        </button>
        <button
          class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          on:click={refreshFeed}
          disabled={loading}
        >
          {#if loading && articles.length === 0}
            refreshing...
          {:else}
            refresh
          {/if}
        </button>
      </div>
    </div>
  {/if}

  {#if error}
    <div class="px-4 py-3 bg-red-50 text-red-700 border-t border-red-200">
      {error}
    </div>
  {/if}

  {#if loading && articles.length === 0}
    <div class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
      loading articles...
    </div>
  {:else if articles.length === 0}
    <div class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
      <p>no articles found</p>
      <p class="mt-2">
        <button
          on:click={refreshFeed}
          class="text-indigo-600 hover:text-indigo-500"
        >
          refresh feed
        </button>
      </p>
    </div>
  {:else}
    <ul class="divide-y divide-gray-200 dark:divide-gray-700">
      {#each articles as article (article.id)}
        <li
          class="px-4 py-4 sm:px-6 hover:bg-gray-50 dark:hover:bg-gray-700 {article.read
            ? 'opacity-75'
            : ''}"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <Link
                to={`/articles/${article.id}`}
                class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium {!article.read
                  ? 'font-bold'
                  : ''}"
              >
                {article.title}
              </Link>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {#if article.author}
                  by {article.author} •
                {/if}
                {formatDate(article.published_at)}
              </p>
            </div>
            <div class="ml-2 flex-shrink-0">
              <button
                on:click={() => toggleReadStatus(article, !article.read)}
                class="p-1 rounded-full text-gray-400 hover:text-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <span class="sr-only"
                  >{article.read ? "mark as unread" : "mark as read"}</span
                >
                {#if article.read}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
                    />
                  </svg>
                {:else}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-5 w-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                {/if}
              </button>
            </div>
          </div>
        </li>
      {/each}
    </ul>

    {#if hasMore}
      <div class="px-4 py-4 sm:px-6 text-center">
        <button
          on:click={loadMore}
          disabled={loading}
          class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600 disabled:opacity-50"
        >
          {loading ? "loading more..." : "load more"}
        </button>
      </div>
    {/if}
  {/if}
</div>
