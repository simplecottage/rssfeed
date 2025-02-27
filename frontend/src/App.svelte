<script>
  import { Router, Route } from "svelte-navigator";
  import FeedList from "./components/FeedList.svelte";
  import ArticleList from "./components/ArticleList.svelte";
  import ArticleView from "./components/ArticleView.svelte";
  import FeedForm from "./components/FeedForm.svelte";
  import Settings from "./components/Settings.svelte";
  import Navbar from "./components/Navbar.svelte";
  import "./app.css";
</script>

<Router>
  <div class="min-h-screen bg-background dark:bg-background-dark font-mono">
    <Navbar />

    <div class="container mx-auto px-4 py-6">
      <Route path="/" component={FeedList} />
      <Route path="/feeds/new" component={FeedForm} />
      <Route path="/feeds/:id/edit" component={FeedForm} />
      <Route path="/feeds/:id" component={ArticleList} />
      <Route path="/articles/:id" component={ArticleView} />
      <Route path="/settings" component={Settings} />
    </div>
  </div>
</Router>

<style>
  :global(body) {
    @apply bg-retro-beige text-gray-800;
  }
</style>
