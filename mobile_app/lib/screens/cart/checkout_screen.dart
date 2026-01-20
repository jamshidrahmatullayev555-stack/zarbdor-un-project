import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:intl/intl.dart';
import '../../providers/language_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/orders_provider.dart';

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _addressController = TextEditingController();
  final _notesController = TextEditingController();
  GoogleMapController? _mapController;
  LatLng? _selectedLocation;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _addressController.dispose();
    _notesController.dispose();
    _mapController?.dispose();
    super.dispose();
  }

  Future<void> _getCurrentLocation() async {
    try {
      final permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        return;
      }

      final position = await Geolocator.getCurrentPosition();
      setState(() {
        _selectedLocation = LatLng(position.latitude, position.longitude);
      });
      _mapController?.animateCamera(
        CameraUpdate.newLatLng(_selectedLocation!),
      );
    } catch (e) {
      print('Error getting location: $e');
    }
  }

  Future<void> _placeOrder() async {
    final address = _addressController.text.trim();
    if (address.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Iltimos, manzilni kiriting')),
      );
      return;
    }

    setState(() => _isLoading = true);

    final cartProvider = Provider.of<CartProvider>(context, listen: false);
    final ordersProvider = Provider.of<OrdersProvider>(context, listen: false);

    final items = cartProvider.items.map((item) => {
      'product_id': item.product.id,
      'quantity': item.quantity,
    }).toList();

    final order = await ordersProvider.createOrder(
      items: items,
      deliveryAddress: address,
      deliveryLat: _selectedLocation?.latitude,
      deliveryLon: _selectedLocation?.longitude,
      notes: _notesController.text.trim(),
    );

    setState(() => _isLoading = false);

    if (order != null && mounted) {
      cartProvider.clear();
      Navigator.of(context).pop();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Buyurtma muvaffaqiyatli yuborildi!')),
      );
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(ordersProvider.error ?? 'Xatolik yuz berdi')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final cartProvider = Provider.of<CartProvider>(context);
    final formatter = NumberFormat('#,##0', 'en_US');

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.translate(lang.checkout)),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Map
                Container(
                  height: 200,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: _selectedLocation != null
                        ? GoogleMap(
                            initialCameraPosition: CameraPosition(
                              target: _selectedLocation!,
                              zoom: 15,
                            ),
                            onMapCreated: (controller) {
                              _mapController = controller;
                            },
                            onTap: (position) {
                              setState(() {
                                _selectedLocation = position;
                              });
                            },
                            markers: {
                              if (_selectedLocation != null)
                                Marker(
                                  markerId: const MarkerId('delivery'),
                                  position: _selectedLocation!,
                                ),
                            },
                          )
                        : const Center(
                            child: CircularProgressIndicator(),
                          ),
                  ),
                ),
                
                const SizedBox(height: 16),
                
                // Address
                TextField(
                  controller: _addressController,
                  decoration: InputDecoration(
                    labelText: lang.translate(lang.deliveryAddress),
                    hintText: lang.isUzbek 
                        ? 'Manzilni kiriting'
                        : 'Введите адрес',
                  ),
                  maxLines: 2,
                ),
                
                const SizedBox(height: 16),
                
                // Notes
                TextField(
                  controller: _notesController,
                  decoration: InputDecoration(
                    labelText: lang.translate(lang.notes),
                    hintText: lang.isUzbek 
                        ? 'Qo\'shimcha izoh (ixtiyoriy)'
                        : 'Дополнительное примечание (необязательно)',
                  ),
                  maxLines: 3,
                ),
                
                const SizedBox(height: 24),
                
                // Order Summary
                Text(
                  lang.isUzbek ? 'Buyurtma tarkibi' : 'Состав заказа',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                
                ...cartProvider.items.map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          '${item.product.getName(lang.currentLanguage)} x${item.quantity}',
                          style: Theme.of(context).textTheme.bodyLarge,
                        ),
                      ),
                      Text(
                        '${formatter.format(item.totalPrice)} ${lang.translate(lang.sum)}',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                    ],
                  ),
                )),
                
                const Divider(height: 32),
                
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      lang.translate(lang.total),
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    Text(
                      '${formatter.format(cartProvider.totalAmount)} ${lang.translate(lang.sum)}',
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
          
          // Bottom Button
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 10,
                  offset: const Offset(0, -5),
                ),
              ],
            ),
            child: SafeArea(
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _placeOrder,
                  child: _isLoading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                          ),
                        )
                      : Text(lang.translate(lang.placeOrder)),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
