import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/routes.dart';
import '../../providers/language_provider.dart';
import '../../providers/products_provider.dart';
import '../../widgets/category_button.dart';
import '../../widgets/product_card.dart';
import '../../widgets/loading_widget.dart';

class HomeTab extends StatefulWidget {
  const HomeTab({super.key});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= 
        _scrollController.position.maxScrollExtent - 200) {
      final provider = Provider.of<ProductsProvider>(context, listen: false);
      if (!provider.isLoading && provider.hasMore) {
        provider.loadProducts();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final productsProvider = Provider.of<ProductsProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.translate(lang.appName)),
        actions: [
          IconButton(
            icon: const Icon(Icons.language),
            onPressed: () {
              Navigator.of(context).pushNamed(AppRoutes.language);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Search Bar
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: lang.translate(lang.search),
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          productsProvider.setSearchQuery('');
                        },
                      )
                    : null,
              ),
              onChanged: (value) {
                productsProvider.setSearchQuery(value);
              },
            ),
          ),
          
          // Categories
          SizedBox(
            height: 50,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: productsProvider.categories.length + 1,
              itemBuilder: (context, index) {
                if (index == 0) {
                  return CategoryButton(
                    name: lang.isUzbek ? 'Barchasi' : 'Все',
                    isSelected: productsProvider.selectedCategoryId == null,
                    onTap: () => productsProvider.setCategory(null),
                  );
                }
                final category = productsProvider.categories[index - 1];
                return CategoryButton(
                  name: category.getName(lang.currentLanguage),
                  isSelected: productsProvider.selectedCategoryId == category.id,
                  onTap: () => productsProvider.setCategory(category.id),
                );
              },
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Products Grid
          Expanded(
            child: productsProvider.products.isEmpty && !productsProvider.isLoading
                ? Center(
                    child: Text(
                      lang.isUzbek ? 'Mahsulotlar topilmadi' : 'Товары не найдены',
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                  )
                : GridView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      childAspectRatio: 0.7,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                    ),
                    itemCount: productsProvider.products.length +
                        (productsProvider.isLoading ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index >= productsProvider.products.length) {
                        return const LoadingWidget();
                      }
                      final product = productsProvider.products[index];
                      return ProductCard(product: product);
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
