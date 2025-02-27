<script>
  import { Link } from "svelte-navigator";
</script>

<nav
  class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700"
>
  <div class="container mx-auto px-4">
    <div class="flex justify-between h-16">
      <div class="flex items-center">
        <Link to="/" class="flex-shrink-0 flex items-center">
          <span class="text-xl font-bold text-gray-800 dark:text-white"
            >RSS Reader</span
          >
        </Link>

        <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
          <Link
            to="/"
            class="border-indigo-500 text-gray-900 dark:text-white inline-flex items-center px-1 pt-1 text-sm font-medium"
          >
            feeds
          </Link>
          <Link
            to="/settings"
            class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white inline-flex items-center px-1 pt-1 text-sm font-medium"
          >
            settings
          </Link>
        </div>
      </div>

      <div class="flex items-center">
        <button
          type="button"
          class="bg-white p-1 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <span class="sr-only">refresh feeds</span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>

        <Link
          to="/feeds/new"
          class="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          add feed
        </Link>
      </div>
    </div>
  </div>
</nav>
