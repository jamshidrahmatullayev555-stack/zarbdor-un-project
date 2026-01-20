import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/routes.dart';
import '../../providers/language_provider.dart';
import '../../providers/auth_provider.dart';

class ProfileTab extends StatelessWidget {
  const ProfileTab({super.key});

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(lang.translate(lang.profile)),
      ),
      body: ListView(
        children: [
          if (authProvider.isAuthenticated) ...[
            UserAccountsDrawerHeader(
              decoration: BoxDecoration(
                color: Theme.of(context).primaryColor,
              ),
              accountName: Text(
                authProvider.user?.fullName ?? '',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              accountEmail: Text(authProvider.user?.phoneNumber ?? ''),
              currentAccountPicture: CircleAvatar(
                backgroundColor: Colors.white,
                child: Text(
                  authProvider.user?.fullName.substring(0, 1).toUpperCase() ?? 'U',
                  style: TextStyle(
                    fontSize: 32,
                    color: Theme.of(context).primaryColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.receipt_long_rounded),
              title: Text(lang.translate(lang.myOrders)),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                Navigator.of(context).pushNamed(AppRoutes.orders);
              },
            ),
            const Divider(),
          ] else ...[
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  const SizedBox(height: 48),
                  Icon(
                    Icons.person_outline_rounded,
                    size: 100,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 24),
                  Text(
                    lang.isUzbek 
                        ? 'Mehmon rejimi'
                        : 'Гостевой режим',
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    lang.isUzbek
                        ? 'Buyurtma berish uchun tizimga kiring'
                        : 'Войдите для оформления заказа',
                    style: Theme.of(context).textTheme.bodyLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed(AppRoutes.login);
                    },
                    child: Text(lang.translate(lang.login)),
                  ),
                  const SizedBox(height: 48),
                ],
              ),
            ),
          ],
          ListTile(
            leading: const Icon(Icons.language_rounded),
            title: Text(lang.translate(lang.language)),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Navigator.of(context).pushNamed(AppRoutes.language);
            },
          ),
          const Divider(),
          if (authProvider.isAuthenticated) ...[
            ListTile(
              leading: const Icon(Icons.logout_rounded),
              title: Text(lang.translate(lang.logout)),
              onTap: () async {
                await authProvider.logout();
              },
            ),
          ],
          const SizedBox(height: 16),
          Center(
            child: Text(
              'Version 1.0.0',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
