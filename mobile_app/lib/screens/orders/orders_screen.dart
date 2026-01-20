import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/routes.dart';
import '../../providers/language_provider.dart';
import '../../providers/orders_provider.dart';
import '../../widgets/order_card.dart';
import '../../widgets/loading_widget.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  @override
  void initState() {
    super.initState();
    _loadOrders();
  }

  Future<void> _loadOrders() async {
    final ordersProvider = Provider.of<OrdersProvider>(context, listen: false);
    await ordersProvider.loadOrders();
  }

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final ordersProvider = Provider.of<OrdersProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.translate(lang.myOrders)),
      ),
      body: ordersProvider.isLoading
          ? const Center(child: LoadingWidget())
          : ordersProvider.orders.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.receipt_long_outlined,
                        size: 100,
                        color: Colors.grey[400],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        lang.isUzbek 
                            ? 'Buyurtmalar yo\'q'
                            : 'Нет заказов',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadOrders,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: ordersProvider.orders.length,
                    itemBuilder: (context, index) {
                      final order = ordersProvider.orders[index];
                      return OrderCard(
                        order: order,
                        onTap: () {
                          Navigator.of(context).pushNamed(
                            AppRoutes.orderDetail,
                            arguments: order,
                          );
                        },
                      );
                    },
                  ),
                ),
    );
  }
}
