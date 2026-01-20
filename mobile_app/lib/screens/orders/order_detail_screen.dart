import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../config/routes.dart';
import '../../models/order.dart';
import '../../providers/language_provider.dart';
import '../../providers/orders_provider.dart';

class OrderDetailScreen extends StatelessWidget {
  const OrderDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final ordersProvider = Provider.of<OrdersProvider>(context);
    final order = ModalRoute.of(context)?.settings.arguments as Order?;
    final formatter = NumberFormat('#,##0', 'en_US');
    final dateFormatter = DateFormat('dd.MM.yyyy HH:mm');

    if (order == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Order not found')),
      );
    }

    final canCancel = order.status == 'pending' || order.status == 'confirmed';

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.isUzbek ? 'Buyurtma #${order.id}' : 'Заказ #${order.id}'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Status Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        lang.isUzbek ? 'Holat' : 'Статус',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 6,
                        ),
                        decoration: BoxDecoration(
                          color: _getStatusColor(order.status),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          order.getStatusText(lang.currentLanguage),
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Text(
                    dateFormatter.format(order.createdAt),
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Delivery Info
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lang.translate(lang.deliveryAddress),
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    order.deliveryAddress,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  if (order.courierName != null) ...[
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.delivery_dining, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          order.courierName!,
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Items
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    lang.isUzbek ? 'Buyurtma tarkibi' : 'Состав заказа',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 16),
                  ...order.items.map((item) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (item.imageUrl != null)
                          ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(
                              item.imageUrl!,
                              width: 60,
                              height: 60,
                              fit: BoxFit.cover,
                            ),
                          ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item.getName(lang.currentLanguage),
                                style: Theme.of(context).textTheme.bodyLarge,
                              ),
                              const SizedBox(height: 4),
                              Text(
                                '${item.quantity} x ${formatter.format(item.price)} ${lang.translate(lang.sum)}',
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                            ],
                          ),
                        ),
                        Text(
                          '${formatter.format(item.totalPrice)} ${lang.translate(lang.sum)}',
                          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  )),
                  const Divider(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        lang.translate(lang.total),
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Text(
                        '${formatter.format(order.totalAmount)} ${lang.translate(lang.sum)}',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Theme.of(context).primaryColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          
          if (order.notes != null && order.notes!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lang.translate(lang.notes),
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      order.notes!,
                      style: Theme.of(context).textTheme.bodyLarge,
                    ),
                  ],
                ),
              ),
            ),
          ],
          
          const SizedBox(height: 24),
          
          // Action Buttons
          if (order.status != 'cancelled' && order.status != 'delivered') ...[
            ElevatedButton.icon(
              onPressed: () {
                Navigator.of(context).pushNamed(
                  AppRoutes.chat,
                  arguments: order.id,
                );
              },
              icon: const Icon(Icons.chat),
              label: Text(lang.translate(lang.chat)),
            ),
            const SizedBox(height: 12),
          ],
          
          if (canCancel)
            OutlinedButton.icon(
              onPressed: () async {
                final confirm = await showDialog<bool>(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: Text(lang.isUzbek 
                        ? 'Buyurtmani bekor qilish' 
                        : 'Отменить заказ'),
                    content: Text(lang.isUzbek
                        ? 'Haqiqatan ham buyurtmani bekor qilmoqchimisiz?'
                        : 'Вы действительно хотите отменить заказ?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: Text(lang.isUzbek ? 'Yo\'q' : 'Нет'),
                      ),
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        child: Text(lang.isUzbek ? 'Ha' : 'Да'),
                      ),
                    ],
                  ),
                );

                if (confirm == true && context.mounted) {
                  final success = await ordersProvider.cancelOrder(order.id);
                  if (success && context.mounted) {
                    Navigator.of(context).pop();
                  }
                }
              },
              icon: const Icon(Icons.cancel),
              label: Text(lang.isUzbek ? 'Bekor qilish' : 'Отменить'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                side: const BorderSide(color: Colors.red),
              ),
            ),
        ],
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending':
        return Colors.orange;
      case 'confirmed':
      case 'preparing':
        return Colors.blue;
      case 'ready':
      case 'picked_up':
      case 'in_transit':
        return Colors.purple;
      case 'delivered':
        return Colors.green;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }
}
