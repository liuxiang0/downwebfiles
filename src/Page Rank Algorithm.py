'''Page Rank Algorithm and Implementation
Difficulty Level : Hard
Last Updated : 06 Nov, 2021
PageRank (PR) is an algorithm used by Google Search to rank websites in their search engine results. PageRank was named after Larry Page, one of the founders of Google. PageRank is a way of measuring the importance of website pages. According to Google:

PageRank works by counting the number and quality of links to a page to determine a rough estimate of how important the website is. The underlying assumption is that more important websites are likely to receive more links from other websites.

It is not the only algorithm used by Google to order search engine results, but it is the first algorithm that was used by the company, and it is the best-known.
The above centrality measure is not implemented for multi-graphs.

Algorithm 
The PageRank algorithm outputs a probability distribution used to represent the likelihood that a person randomly clicking on links will arrive at any particular page. PageRank can be calculated for collections of documents of any size. It is assumed in several research papers that the distribution is evenly divided among all documents in the collection at the beginning of the computational process. The PageRank computations require several passes, called “iterations”, through the collection to adjust approximate PageRank values to more closely reflect the theoretical true value.

Simplified algorithm 
Assume a small universe of four web pages: A, B, C, and D. Links from a page to itself, or multiple outbound links from one single page to another single page, are ignored. PageRank is initialized to the same value for all pages. In the original form of PageRank, the sum of PageRank over all pages was the total number of pages on the web at that time, so each page in this example would have an initial value of 1. However, later versions of PageRank, and the remainder of this section, assume a probability distribution between 0 and 1. Hence the initial value for each page in this example is 0.25.
The PageRank transferred from a given page to the targets of its outbound links upon the next iteration is divided equally among all outbound links.
If the only links in the system were from pages B, C, and D to A, each link would transfer 0.25 PageRank to A upon the next iteration, for a total of 0.75.
PR(A) = PR(B) + PR(C) + PR(D).\,  
Suppose instead that page B had a link to pages C and A, page C had a link to page A, and page D had links to all three pages. Thus, upon the first iteration, page B would transfer half of its existing value, or 0.125, to page A and the other half, or 0.125, to page C. Page C would transfer all of its existing value, 0.25, to the only page it links to, A. Since D had three outbound links, it would transfer one-third of its existing value, or approximately 0.083, to A. At the completion of this iteration, page A will have a PageRank of approximately 0.458. 
PR(A)={\frac {PR(B)}{2}}+{\frac {PR(C)}{1}}+{\frac {PR(D)}{3}}.\,  
In other words, the PageRank conferred by an outbound link is equal to the document’s own PageRank score divided by the number of outbound links L( ).
PR(A)={\frac {PR(B)}{L(B)}}+{\frac {PR(C)}{L(C)}}+{\frac {PR(D)}{L(D)}}.\,  In the general case, the PageRank value for any page u can be expressed as:
PR(u) = \sum_{v \in B_u} \frac{PR(v)}{L(v)}  ,
i.e. the PageRank value for a page u is dependent on the PageRank values for each page v contained in the set Bu (the set containing all pages linking to page u), divided by the number L(v) of links from page v. The algorithm involves a damping factor for the calculation of the PageRank. It is like the income tax which the govt extracts from one despite paying him itself.

Following is the code for the calculation of the Page rank. 
'''

def pagerank(G, alpha=0.85, personalization=None,
			max_iter=100, tol=1.0e-6, nstart=None, weight='weight',
			dangling=None):
	"""Return the PageRank of the nodes in the graph.

	PageRank computes a ranking of the nodes in the graph G based on
	the structure of the incoming links. It was originally designed as
	an algorithm to rank web pages.

	Parameters
	----------
	G : graph
	A NetworkX graph. Undirected graphs will be converted to a directed
	graph with two directed edges for each undirected edge.

	alpha : float, optional
	Damping parameter for PageRank, default=0.85.

	personalization: dict, optional
	The "personalization vector" consisting of a dictionary with a
	key for every graph node and nonzero personalization value for each node.
	By default, a uniform distribution is used.

	max_iter : integer, optional
	Maximum number of iterations in power method eigenvalue solver.

	tol : float, optional
	Error tolerance used to check convergence in power method solver.

	nstart : dictionary, optional
	Starting value of PageRank iteration for each node.

	weight : key, optional
	Edge data key to use as weight. If None weights are set to 1.

	dangling: dict, optional
	The outedges to be assigned to any "dangling" nodes, i.e., nodes without
	any outedges. The dict key is the node the outedge points to and the dict
	value is the weight of that outedge. By default, dangling nodes are given
	outedges according to the personalization vector (uniform if not
	specified). This must be selected to result in an irreducible transition
	matrix (see notes under google_matrix). It may be common to have the
	dangling dict to be the same as the personalization dict.

	Returns
	-------
	pagerank : dictionary
	Dictionary of nodes with PageRank as value

	Notes
	-----
	The eigenvector calculation is done by the power iteration method
	and has no guarantee of convergence. The iteration will stop
	after max_iter iterations or an error tolerance of
	number_of_nodes(G)*tol has been reached.

	The PageRank algorithm was designed for directed graphs but this
	algorithm does not check if the input graph is directed and will
	execute on undirected graphs by converting each edge in the
	directed graph to two edges.

	
	"""
	if len(G) == 0:
		return {}

	if not G.is_directed():
		D = G.to_directed()
	else:
		D = G

	# Create a copy in (right) stochastic form
	W = nx.stochastic_graph(D, weight=weight)
	N = W.number_of_nodes()

	# Choose fixed starting vector if not given
	if nstart is None:
		x = dict.fromkeys(W, 1.0 / N)
	else:
		# Normalized nstart vector
		s = float(sum(nstart.values()))
		x = dict((k, v / s) for k, v in nstart.items())

	if personalization is None:

		# Assign uniform personalization vector if not given
		p = dict.fromkeys(W, 1.0 / N)
	else:
		missing = set(G) - set(personalization)
		if missing:
			raise NetworkXError('Personalization dictionary '
								'must have a value for every node. '
								'Missing nodes %s' % missing)
		s = float(sum(personalization.values()))
		p = dict((k, v / s) for k, v in personalization.items())

	if dangling is None:

		# Use personalization vector if dangling vector not specified
		dangling_weights = p
	else:
		missing = set(G) - set(dangling)
		if missing:
			raise NetworkXError('Dangling node dictionary '
								'must have a value for every node. '
								'Missing nodes %s' % missing)
		s = float(sum(dangling.values()))
		dangling_weights = dict((k, v/s) for k, v in dangling.items())
	dangling_nodes = [n for n in W if W.out_degree(n, weight=weight) == 0.0]

	# power iteration: make up to max_iter iterations
	for _ in range(max_iter):
		xlast = x
		x = dict.fromkeys(xlast.keys(), 0)
		danglesum = alpha * sum(xlast[n] for n in dangling_nodes)
		for n in x:

			# this matrix multiply looks odd because it is
			# doing a left multiply x^T=xlast^T*W
			for nbr in W[n]:
				x[nbr] += alpha * xlast[n] * W[n][nbr][weight]
			x[n] += danglesum * dangling_weights[n] + (1.0 - alpha) * p[n]

		# check convergence, l1 norm
		err = sum([abs(x[n] - xlast[n]) for n in x])
		if err < N*tol:
			return x
	raise NetworkXError('pagerank: power iteration failed to converge '
						'in %d iterations.' % max_iter)

'''
import networkx as nx
>>> G=nx.barabasi_albert_graph(60,41)
>>> pr=nx.pagerank(G,0.4)
>>> pr

The above code has been run on IDLE(Python IDE of windows). You would need to download the networkx library before you run this code. The part inside the curly braces represents the output. It is almost similar to Ipython(for Ubuntu users).

References 

https://en.wikipedia.org/wiki/PageRank
http://networkx.readthedocs.io/en/networkx-1.10/index.html
https://www.geeksforgeeks.org/ranking-google-search-works/
https://www.geeksforgeeks.org/google-search-works/

Thus, this way the centrality measure of Page Rank is calculated for the given graph. This way we have covered 2 centrality measures. I would like to write further on the various centrality measures used for the network analysis.
This article is contributed by [Jayant Bisht](https://in.linkedin.com/in/jayant-bisht-978085114). If you like GeeksforGeeks and would like to contribute, you can also write an article using [write.geeksforgeeks.org](https://write.geeksforgeeks.org/) or mail your article to review-team@geeksforgeeks.org. See your article appearing on the GeeksforGeeks main page and help other Geeks.
Please write comments if you find anything incorrect, or you want to share more information about the topic discussed above.
'''