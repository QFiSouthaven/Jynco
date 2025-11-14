/**
 * ChromaFrame - 2D Flip-Book Animator
 * Main Entry Point
 *
 * Copyright (c) 2025 Video Foundry Team
 * Licensed under MIT License
 */

#include <QApplication>
#include <QMessageBox>
#include <iostream>

// Placeholder - will include actual headers when implemented
// #include "chromaframe/Application.h"
// #include "chromaframe/MainWindow.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);

    // Set application metadata
    QApplication::setApplicationName("ChromaFrame");
    QApplication::setApplicationVersion("0.1.0");
    QApplication::setOrganizationName("Video Foundry");
    QApplication::setOrganizationDomain("videofoundry.dev");

    std::cout << "ChromaFrame v0.1.0" << std::endl;
    std::cout << "====================" << std::endl;
    std::cout << "Status: Design Phase" << std::endl;
    std::cout << "" << std::endl;
    std::cout << "ChromaFrame is currently in the design phase." << std::endl;
    std::cout << "Implementation will begin in Q1 2025." << std::endl;
    std::cout << "" << std::endl;
    std::cout << "See docs/CHROMAFRAME_ARCHITECTURE.md for details." << std::endl;

    // Show message box
    QMessageBox::information(
        nullptr,
        "ChromaFrame",
        "ChromaFrame is currently in the design phase.\n\n"
        "Implementation will begin in Q1 2025.\n\n"
        "See docs/CHROMAFRAME_ARCHITECTURE.md for details."
    );

    // Placeholder - will create and show main window when implemented
    // ChromaFrame::Application chromaApp;
    // chromaApp.initialize();
    // chromaApp.showMainWindow();
    // return app.exec();

    return 0;
}
