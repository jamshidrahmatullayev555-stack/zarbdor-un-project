import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/language_provider.dart';

class LanguageScreen extends StatelessWidget {
  const LanguageScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final languageProvider = Provider.of<LanguageProvider>(context);
    final currentLanguage = languageProvider.language;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          currentLanguage == 'uz' ? 'Til' : 'Язык',
        ),
      ),
      body: ListView(
        children: [
          RadioListTile<String>(
            title: const Text('O\'zbekcha'),
            subtitle: const Text('Uzbek'),
            value: 'uz',
            groupValue: currentLanguage,
            activeColor: const Color(0xFFF97316),
            onChanged: (value) {
              if (value != null) {
                languageProvider.setLanguage(value);
                Navigator.pop(context);
              }
            },
          ),
          const Divider(height: 1),
          RadioListTile<String>(
            title: const Text('Русский'),
            subtitle: const Text('Russian'),
            value: 'ru',
            groupValue: currentLanguage,
            activeColor: const Color(0xFFF97316),
            onChanged: (value) {
              if (value != null) {
                languageProvider.setLanguage(value);
                Navigator.pop(context);
              }
            },
          ),
        ],
      ),
    );
  }
}
