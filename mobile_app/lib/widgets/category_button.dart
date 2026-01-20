import 'package:flutter/material.dart';

class CategoryButton extends StatelessWidget {
  final String name;
  final bool isSelected;
  final VoidCallback onTap;

  const CategoryButton({
    super.key,
    required this.name,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          decoration: BoxDecoration(
            color: isSelected
                ? Theme.of(context).primaryColor
                : Colors.grey[200],
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            name,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.black87,
              fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }
}
