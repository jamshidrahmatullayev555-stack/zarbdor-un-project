import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../providers/language_provider.dart';

class NoInternetScreen extends StatelessWidget {
  const NoInternetScreen({super.key});

  Future<void> _retry(BuildContext context) async {
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity != ConnectivityResult.none) {
      if (context.mounted) {
        Navigator.of(context).pop();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = Provider.of<LanguageProvider>(context);

    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.wifi_off_rounded,
                size: 100,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 24),
              Text(
                lang.translate(lang.noInternet),
                style: Theme.of(context).textTheme.headlineMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 48),
              ElevatedButton.icon(
                onPressed: () => _retry(context),
                icon: const Icon(Icons.refresh),
                label: Text(lang.translate(lang.retry)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
