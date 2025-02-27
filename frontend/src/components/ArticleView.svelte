<script>
  import { onMount } from 'svelte';
  import { useParams, Link } from 'svelte-navigator';
  import { articleService } from '../services/api';
  import { format } from 'date-fns';
  
  const params = useParams();
  
  let article = null;
  let loading = true;
  let loadingFullContent = false;
  let error = null;
  let fullContentError = null;
  let showOriginal = false;
  
  onMount(async () => {
    try {
      article = await articleService.getById($params.id);
      
      // Mark as read automatically
      if (!article.read) {
        await articleService.markAsRead(article.id, true);
        article.read = true;
      }
      
      // If article has full content, great! If not, try to fetch it
      if (!article.full_content) {
        loadFullContent();
      }
      
      loading = false;
    } catch (err) {
      error = err.message || 'Failed to load article';
      loading = false;
    }
  });
  
  async function loadFullContent() {
    loadingFullContent = true;
    fullContentError = null;
    
    try {
      const fullArticle = await articleService.getFullContent(article.id);
      article = {...article, ...fullArticle};
      loadingFullContent = false;
    } catch (err) {
      fullContentError = err.message || 'Failed to load full article content';
      loadingFullContent = false;
    }
  }
  
  function formatDate(dateString) {
    if (!dateString) return 'Unknown date';
    
    try {
      const date = new Date(dateString);
      return format(date, 'MMMM d, yyyy h:mm a');
    } catch (err) {
      return 'Invalid date';
    }
  }
  
  function toggleContentView() {
    showOriginal = !showOriginal;
  }
</script>

<div class="bg-white dark:bg-gray-800 shadow sm:rounded-lg">
  {#if loading}
    <div class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
      loading article...
    </div>
  {:else if error}
    <div class="px-4 py-5 sm:p-6">
      <div class="bg-red-50 text-red-700 p-4 rounded-md">
        {error}
      </div>
      <div class="mt-4">
        <Link to="/" class="text-indigo-600 hover:text-indigo-500">
          back to feeds
        </Link>
      </div>
    </div>
  {:else if article}
    <div class="px-4 py-5 sm:p-6">
      <div class="mb-6">
        <Link to={`/feeds/${article.feed_id}`} class="text-sm text-indigo-600 hover:text-indigo-500">
          ← back to {article.feed_title || 'feed'}
        </Link>
      </div>
      
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
        {article.title}
      </h1>
      
      <div class="flex items-center text-sm text-gray-500 dark:text-gray-400 mb-4">
        {#if article.author}
          <span class="mr-2">by {article.author}</span>
          <span class="mx-2">•</span>
        {/if}
        <span>{formatDate(article.published_at)}</span>
        
        <div class="ml-auto flex space-x-2">
          <button 
            on:click={toggleContentView}
            class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
          >
            {showOriginal ? 'show full article' : 'show summary'}
          </button>
          
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
            class="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600 dark:hover:bg-gray-600"
          >
            view on site
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
      
      {#if showOriginal}
        <!-- Show original summary content -->
        {#if article.content}
          <div class="prose dark:prose-invert max-w-none article-content">
            {@html article.content}
          </div>
        {:else}
          <div class="py-4 text-gray-500 dark:text-gray-400 italic">
            No summary available. Please view the full article.
          </div>
        {/if}
      {:else}
        <!-- Show full content when available -->
        {#if article.full_content}
          <div class="prose dark:prose-invert max-w-none article-content">
            {@html article.full_content}
          </div>
        {:else if loadingFullContent}
          <div class="py-8 text-center">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p class="mt-2 text-gray-500 dark:text-gray-400">loading full article content...</p>
          </div>
        {:else if fullContentError}
          <div class="p-4 bg-yellow-50 text-yellow-700 rounded-md mb-4">
            <p>We couldn't extract the full article content. <span class="font-semibold">Error:</span> {fullContentError}</p>
            <p class="mt-2">
              <button 
                on:click={loadFullContent} 
                class="text-indigo-600 hover:text-indigo-500 underline"
              >
                Try again
              </button> or 
              <a 
                href={article.url} 
                target="_blank"
                rel="noopener noreferrer" 
                class="text-indigo-600 hover:text-indigo-500 underline"
              >
                view the original page
              </a>
            </p>
          </div>
          
          {#if article.content}
            <div class="prose dark:prose-invert max-w-none article-content">
              {@html article.content}
            </div>
          {:else}
            <div class="py-4 text-gray-500 dark:text-gray-400 italic">
              No content available. Please visit the original article.
            </div>
          {/if}
        {:else}
          <div class="py-8 text-center">
            <button
              on:click={loadFullContent}
              class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Load full article
            </button>
            <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
              This will extract the article content so you can read it here.
            </p>
          </div>
          
          {#if article.content}
            <div class="mt-6 p-4 border border-gray-200 dark:border-gray-700 rounded-md">
              <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-3">Article summary:</h3>
              <div class="prose dark:prose-invert max-w-none article-content">
                {@html article.content}
              </div>
            </div>
          {/if}
        {/if}
      {/if}
    </div>
  {/if}
</div>

<style>
  :global(.article-content img) {
    max-width: 100%;
    height: auto;
  }
  
  :global(.article-content a) {
    color: #4f46e5;
    text-decoration: underline;
  }
  
  :global(.article-content pre) {
    background-color: #f3f4f6;
    padding: 1rem;
    border-radius: 0.375rem;
    overflow-x: auto;
  }
  
  :global(.dark .article-content pre) {
    background-color: #374151;
  }
</style>
